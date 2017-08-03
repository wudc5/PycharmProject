package com.cwl.spark.ml.job

import com.cwl.spark.ml.utils.GetUUID.getUUID
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.regression.{LabeledPoint, LinearRegressionWithSGD}
import com.cwl.spark.ml.utils.TimeHelper.getCurrentTime
/**
  * Created by wdc on 2017/6/10.
  */
object SaleForecastJob extends SparkBaseJob{

  /**
    *期号和销售额字段格式
    */
  case class resultset_lp(drawnum:Int,
                          saleamount: Double
                      )

  /**
    *统计结果字段格式
    */
  case class resultset_statis(uuid:String,
                              drawnum: Int,
                              preds_time:String,
                              provincename:String,
                              provinceid:String,
                              cityname:String,
                              cityid:String,
                              gamename:String,
                              gameid:String,
                              period: String,
                              forecast_amount: Double,
                              true_amount: Double
                      )

  override def runJob: Unit ={
    val gamelist = List("双色球","七乐彩")
    val drawnumlist = List(2017053, 2017054, 2017055, 170510066)
    val drawsale_DF = hiveContext.read.jdbc(gp_url, "drawsalegrandtotal", props)
    drawsale_DF.registerTempTable("drawsaleTable")
    val citylist = hiveContext.sql("select distinct(cityname) as cityname from drawsaleTable").collectAsList()
    log.info("citylist: "+citylist)
    for(i <- 0 until citylist.size() - 1){
      val city = citylist.get(i).getAs[String]("cityname")
      if(city != null){
        log.info("city: " + city)
        for(game <- gamelist){
          log.info("game: " + game)
          for(drawnum <- drawnumlist){
            log.info("drawnum: "+ drawnum)

            // 通过前3期的销售额预测该期
            val drawnum1 = (drawnum - 1).toString
            val drawnum2 = (drawnum - 2).toString
            val drawnum3 = (drawnum - 3).toString
            val sql1 = String.format("select sum(drawsaleamount) as saleamount from drawsaleTable where cityname = '%s' and gamename = '%s' and saledrawnumber = '%s'", city, game, drawnum1)
            val sql2 = String.format("select sum(drawsaleamount) as saleamount from drawsaleTable where cityname = '%s' and gamename = '%s' and saledrawnumber = '%s'", city, game, drawnum2)
            val sql3 = String.format("select sum(drawsaleamount) as saleamount from drawsaleTable where cityname = '%s' and gamename = '%s' and saledrawnumber = '%s'", city, game, drawnum3)
            log.info("sql1: "+sql1)
            log.info("sql2: "+sql2)
            log.info("sql3: "+sql3)
            var saleamount1 = 0.00
            var saleamount2 = 0.00
            var saleamount3 = 0.00
            val saleamount1_tmp = hiveContext.sql(sql1).first().getAs[java.math.BigDecimal]("saleamount")
            val saleamount2_tmp = hiveContext.sql(sql2).first().getAs[java.math.BigDecimal]("saleamount")
            val saleamount3_tmp = hiveContext.sql(sql3).first().getAs[java.math.BigDecimal]("saleamount")
            if(saleamount1_tmp == null){
              val sql4 = String.format("select avg(drawsaleamount) as avggameamount from drawsaleTable where cityname = '%s' and gamename = '%s'", city, game)
              log.info("sql4: "+sql4)
              val avggameamount = hiveContext.sql(sql4).first().getAs[java.math.BigDecimal]("avggameamount")
              if(avggameamount == null){
                val sql5 = String.format("select avg(drawsaleamount) as avgcityamount from drawsaleTable where cityname = '%s'", city)
                log.info("sql5: "+sql5)
                val avgcityamount = hiveContext.sql(sql5).first().getAs[java.math.BigDecimal]("avgcityamount").toString.toDouble
                saleamount1 = avgcityamount
              }else{
                saleamount1 = avggameamount.toString.toDouble
              }
            }else{
              saleamount1 = saleamount1_tmp.toString.toDouble
            }

            if(saleamount2_tmp == null){
              val sql6 = String.format("select avg(drawsaleamount) as avggameamount from drawsaleTable where cityname = '%s' and gamename = '%s'", city, game)
              log.info("sql6: "+sql6)
              val avggameamount = hiveContext.sql(sql6).first().getAs[java.math.BigDecimal]("avggameamount")
              if(avggameamount == null){
                val sql7 = String.format("select avg(drawsaleamount) as avgcityamount from drawsaleTable where cityname = '%s'", city)
                log.info("sql7: "+sql7)
                val avgcityamount = hiveContext.sql(sql7).first().getAs[java.math.BigDecimal]("avgcityamount").toString.toDouble
                saleamount2 = avgcityamount
              }else{
                saleamount2 = avggameamount.toString.toDouble
              }
            }else{
              saleamount2 = saleamount2_tmp.toString.toDouble
            }

            if(saleamount3_tmp == null){
              val sql8 = String.format("select avg(drawsaleamount) as avggameamount from drawsaleTable where cityname = '%s' and gamename = '%s'", city, game)
              log.info("sql8: "+sql8)
              val avggameamount = hiveContext.sql(sql8).first().getAs[java.math.BigDecimal]("avggameamount")
              if(avggameamount == null){
                val sql9 = String.format("select avg(drawsaleamount) as avgcityamount from drawsaleTable where cityname = '%s'", city)
                log.info("sql9: "+sql9)
                val avgcityamount = hiveContext.sql(sql9).first().getAs[java.math.BigDecimal]("avgcityamount").toString.toDouble
                saleamount3 = avgcityamount
              }else{
                saleamount3 = avggameamount.toString.toDouble
              }
            }else{
              saleamount3 = saleamount3_tmp.toString.toDouble
            }
            val train_data = List(resultset_lp(1, saleamount1), resultset_lp(2, saleamount2), resultset_lp(3, saleamount3))
            val train_DF = hiveContext.createDataFrame(train_data)
            val parsedData = train_DF.map{ row =>
              LabeledPoint(row.getAs[Double]("saleamount"), Vectors.dense(row.getAs[Int]("drawnum")))
            }

            // 建立模型，进行预测
            val model = LinearRegressionWithSGD.train(parsedData, 100, 0.1)
            val pattern = new java.text.DecimalFormat("#.##")
            val forecast_amount = pattern.format(model.predict(Vectors.dense(4))).toDouble

            // 得到真实销售额
            val sql10 = String.format("select sum(drawsaleamount) as saleamount from drawsaleTable where cityname = '%s' and gamename = '%s' and saledrawnumber = '%s'", city, game, drawnum.toString)
            log.info("sql10: "+sql10)
            val true_amount_tmp = hiveContext.sql(sql10).first().getAs[java.math.BigDecimal]("saleamount")
            var true_amount = 0.0
            if(true_amount_tmp == null){
              true_amount = 0
            }else{
              true_amount = true_amount_tmp.toString.toDouble
            }
            log.info(drawnum1+ "的销售额为: " + saleamount1)
            log.info(drawnum2+ "的销售额为: " + saleamount2)
            log.info(drawnum3+ "的销售额为: " + saleamount3)
            log.info(drawnum + "的预测销售额为: "+ forecast_amount)
            log.info(drawnum + "的真实销售额为: "+ true_amount)

            // 保存结果
            val sql11 = String.format("select provinceid, provincename, cityid from drawsaleTable where cityname = '%s'", city)
            log.info("sql11: "+sql11)
            val provinceid = hiveContext.sql(sql11).first().getAs[String]("provinceid")
            val provincename = hiveContext.sql(sql11).first().getAs[String]("provincename")
            val cityid = hiveContext.sql(sql11).first().getAs[String]("cityid")
            val sql12 = String.format("select gameid from drawsaleTable where gamename = '%s'", game)
            log.info("sql12: "+sql12)
            val gameid = hiveContext.sql(sql12).first().getAs[String]("gameid")
            val uuid = getUUID()
            val statis_res = List(resultset_statis(uuid, drawnum, getCurrentTime().split(" ")(0), provincename, provinceid, city, cityid, game, gameid, "draw", forecast_amount, true_amount))
            val res_DF = hiveContext.createDataFrame(statis_res)
            res_DF.write.mode("append").jdbc(gp_url, "saleforecast", props)
          }
        }
      }
    }
  }
  def main(args: Array[String]): Unit = {
    runJob
  }
}