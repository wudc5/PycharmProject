package com.cwl.spark.ml.job

import org.apache.spark.ml.feature.StringIndexerModel
import com.cwl.spark.ml.features.MergeFeatures.mergeFeatures
import com.cwl.spark.ml.utils.TimeHelper.getCurrentTime
import com.cwl.spark.ml.utils.DBHelper.getdataFromPostgresql
import org.apache.spark.ml.feature.MinMaxScalerModel
import org.apache.spark.mllib.tree.model.RandomForestModel
import org.apache.spark.sql.{Row, SaveMode}
import org.apache.spark.sql.types.{StringType, StructField, StructType, IntegerType}
import com.cwl.spark.ml.utils.GetUUID.getUUID
import org.apache.spark.sql.AnalysisException
import org.postgresql.util.PSQLException
import java.util.Random
/**
  * Created by wdc on 2017/3/20.
  */
object PredictJob extends SparkBaseJob{

  def main(args: Array[String]): Unit = {
    runJob
  }

  override def runJob: Unit = {
    /**
      *  得到最新model的保存路径
      */
    val dm_modelinfo_DF = hiveContext.read.jdbc(gp_url, "dm_modelinfo", props)
    val filepath = dm_modelinfo_DF.where("model_type = '分类模型'").orderBy(dm_modelinfo_DF("start_time").desc).first().getAs[String]("model_file_path")

    //  随机获取一万条数据进行预测
    val waitpreds_DF = hiveContext.read.jdbc(gp_url,"antiaddiction_train",props)
    waitpreds_DF.registerTempTable("tmpTable")
    val totalnum = hiveContext.sql("select count(*) as count from tmpTable").first().getAs[Long]("count").toString.toInt
    val max = (new util.Random).nextInt(totalnum-10001)
    val min = 1000001
    val random = new Random()
    val rdnum = random.nextInt(max)%(max-min+1) + min
    val tmp_DF = hiveContext.sql("select * from tmpTable where account > "+rdnum+" and account < " + (rdnum+10000))  //测试数据

    //  性别数值化
    val stringIndexModel = StringIndexerModel.load(filepath+"genderIndexModel")
    val genderScaled_DF = stringIndexModel.transform(tmp_DF)

    //  合并特征
    val waitMergeCols = Array(
                              "age",
                              "Indexed_gender",
                              "avgdailyvisit",
                              "avgdailyvisittime",
                              "ratioofvisitwith3page",
                              "avgdailyvisitsatworktime",
                              "avgdailyvisitsatofftime",
                              "avgdailymoney",
                              "avgweekvisitsatofftime",
                              "maxdailymoney",
                              "avgbetmultiple",
                              "maxbetmultiple",
                              "avgweekbuycount"
    )
    val mergedFeat_DF = mergeFeatures(genderScaled_DF, waitMergeCols)

    //  load minmaxScaler Model and do minmax transformation
    val minmaxModel = MinMaxScalerModel.load(filepath + "MinMaxScalerModel")
    val scaledData = minmaxModel.transform(mergedFeat_DF)

    // 记录每个用户最近一次的状态值
    var accAndstatus:scala.collection.Map[scala.Predef.String,Int] = Map()
    try{
      hiveContext.read.jdbc(gp_url,"antiaddiction_result",props).registerTempTable("t1")
      hiveContext.sql("select max(preds_time) as preds_time, account from t1 group by account").registerTempTable("t2")
      accAndstatus = hiveContext.sql("select t1.account as account, t1.status as status from t1 join t2 on t1.account = t2.account").select("account", "status").map{row=> (row.getAs[String]("account"), row.getAs[Int]("status"))}.collectAsMap()
    }catch {
      case ex: AnalysisException=>{
        log.info(ex.getMessage)
    } case ex: PSQLException => {
        log.info(ex.getMessage)
      }
      case ex: java.lang.IllegalArgumentException=>{
        log.info(ex.getMessage)
      }
    }

    // load randomforest Model and Predict
    val modelinfoDF = getdataFromPostgresql("dm_modelinfo", sqlContext, gp_url)
    val model_uuid = modelinfoDF.filter("model_type = '分类模型'").orderBy(modelinfoDF("start_time").desc).first().getAs[String]("model_record_uuid")
    val algorithm = modelinfoDF.filter("model_type = '分类模型'").orderBy(modelinfoDF("start_time").desc).first().getAs[String]("algorithm")
    val randomforestModel = RandomForestModel.load(sparkContext, filepath+"RandomForestClassificationModel")
    val res_rdd = scaledData.map{point =>
      val preds_time = getCurrentTime()
      val result_uuid = getUUID()
      val account = point.getAs[String]("account")
      val provinceid = point.getAs[String]("provinceid")
      val provincename = point.getAs[String]("provincename")
      var status = 0   //初始化当前这次状态为0，如果之前状态不是0，则此次状态值加1，否则此次状态值设为0
      var statusbefore = 0
      if(accAndstatus.contains(account)){
        statusbefore = accAndstatus(account).toString.toInt
      }
      val prediction_label = randomforestModel.predict(point.getAs[org.apache.spark.mllib.linalg.Vector]("MinMaxScalerFeatures"))
      var prediction = ""
      if(prediction_label == 0){
        prediction = "正常"
      }else if (prediction_label == 1){
        prediction = "轻度沉迷"
      }else if (prediction_label == 2){
        prediction = "中度沉迷"
      }else{
        prediction = "重度沉迷"
        status = statusbefore + 1
      }
      Row(result_uuid, model_uuid, algorithm, account, provinceid, provincename, prediction, preds_time, status)
    }
    val schema = StructType(
      Array(StructField("result_uuid", StringType, nullable = true),
      StructField("model_uuid", StringType, nullable = true),
      StructField("algorithm", StringType, nullable = true),
      StructField("account", StringType, nullable = true),
      StructField("provinceid", StringType, nullable = true),
      StructField("provincename", StringType, nullable = true),
      StructField("prediction", StringType, nullable = true),
      StructField("preds_time", StringType, nullable = true),
      StructField("status", IntegerType, nullable = true)
      )
    )
    val res_DF = sqlContext.createDataFrame(res_rdd, schema)

    // save result
    res_DF.write.mode(SaveMode.Append).jdbc(gp_url, "antiaddiction_result", props)
  }
}
