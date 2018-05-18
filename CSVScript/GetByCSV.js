/*
  通过修改filePath来选择源文件，之后启动脚本即可
 */

var https = require('https');
var fs = require('fs');
var readline = require('readline');
var os = require('os');

const TOKEN = 'EAAIzxloXbZCEBALoTpDg2QGasR9JvCR41oAl44OIClJxr7uikwI0PNHxyU0MYHvgNKwPCDOiiZACrKZA72c5ckYlALHybCue9NABpzANvjWsONWQWMqhZA95rPCvtWfftbGcTZByObOZBUJjW9lcPlpNLeHi2ZC2ZAUZD';

var filePath = "./interest_keyword.csv";
var outputPath = "./output.csv";
var fRead = fs.createReadStream(filePath);
var fWrite = fs.createWriteStream(outputPath);

var set = new Set();
var pathSet = new Set();
var stack = [];

var getData = function(name, type) {
      //文件单行读取完毕
      if (name !== 'Name' && type !== 'type'){
            var url = "https://graph.facebook.com/v2.11/search?access_token="+ TOKEN + "&type=adinterest"+ "&q=" + name;
            //向服务器发起请求，获得单行查询结果
            var get = https.get(url, function (response) {
                //console.log(response.headers['content-type']);
                  var body = [];
                  response.on('timeout', function() {
                    if (stack.length > 0){
                      console.log("发生超时");
                      var tempArray = stack.shift();
                      console.log("name:" + tempArray[0] +" type:"+ tempArray[1]);
                      setTimeout(getData(tempArray[0], tempArray[1]), 5000);
                    }
                  });
                  //存储查询数据
                  response.on('data', function (chunk) {
                    body.push(chunk);
                  });
                  //处理数据
                  response.on('end', function () {
                    //获得body部分
                    body = Buffer.concat(body);
                    //get.end();
                    try {
                      //解析body为具体的json数组
                      let bodyData = JSON.parse(body.toString());

                      for(let i = 0; i < bodyData.data.length; i++){
                        //取得其中一条数据，根据id判重
                        if (!set.has(bodyData.data[i].id)){
                          set.add(bodyData.data[i].id);
                          let temp = bodyData.data[i].id + "," + bodyData.data[i].name + "," + type + os.EOL;
                          fWrite.write(temp);
                          //如果当前条目不是重复的条目，需要先查询name
                          let name = bodyData.data[i].name;
                          let nameArray = name.toString().split(' ');
                          //console.log("name::::" + name)
                          for (let i = 0; i < nameArray.length; i++){
                            if (!pathSet.has(nameArray[i])){
                              pathSet.add(nameArray[i]);
                              stack.push([nameArray[i], ""]);
                            }
                          }
                          for(let j = 0; j < bodyData.data[i].path.length; j++){
                            //path条目需要判重
                            let path = bodyData.data[i].path[j];
                            //console.log("path::::" + path)
                            let pathArray = path.toString().split(' ');
                            for (let k = 0; k < pathArray.length; k++){
                              if (!pathSet.has(pathArray[k])){
                                pathSet.add(pathArray[k]);
                                stack.push([pathArray[k], ""]);
                              }
                            }
                          }
                          //搜索topic选项
                          let topic = bodyData.data[i].topic;
                          if (typeof(topic) !== "undefined"){
                            //console.log("topic::::" + topic);
                            let topicArray = topic.toString().split(' ');
                            for (let l = 0; l < topicArray.length; l++){
                              if (!pathSet.has(topicArray[l])){
                                pathSet.add(topicArray[l]);
                                stack.push([topicArray[l], ""]);
                              }
                            }
                          }

                        }
                      }
                      if (stack.length > 0){
                        var tempArray = stack.shift();
                        console.log("name:" + tempArray[0] +" type:"+ tempArray[1]);
                        getData(tempArray[0], tempArray[1]);
                      }
                    }catch (e) {
                      console.log("error");
                      if (stack.length > 0){
                        var tempArray = stack.shift();
                        console.log("name:" + tempArray[0] +" type:"+ tempArray[1]);
                        getData(tempArray[0], tempArray[1]);
                      }
                    }
                  });
            });

      }
};
var getResult = function () {
    var objReadline = readline.createInterface({
            input: fRead,
            output: fWrite,
        }
    );
    var title = "id" + ",name" + ",type" + os.EOL;
    fWrite.write(title);

    //逐行读取，当每次遇到\n时会自动触发下面的事件
    objReadline.on('line', function (line) {
        let lineArray = line.toString().split(',');
        let name = lineArray[0];
        let type = lineArray[1];
        if (name === 'Name' && type === 'Type'){
          return;
        }
        let nameArray = name.split(' ');
        let typeArray = type.split(' ');
        for (let i = 0; i < nameArray.length; i++){
          if (!pathSet.has(nameArray[i])){
            pathSet.add(nameArray[i]);
            stack.push([nameArray[i], type]);
          }
        }
        for (let i = 0; i < typeArray.length; i++){
          if (!pathSet.has(typeArray[i])){
            pathSet.add(typeArray[i]);
            stack.push([typeArray[i], ""]);
          }
        }
    });
    //文件读取完毕
    objReadline.on('close', function () {
        let tempArray = stack.shift();
        getData(tempArray[0], tempArray[1]);
    });
};
try {
  getResult();
} catch (e) {
  console.log("连接出现异常");
  if (stack.length > 0){
    let tempArray = stack.shift();
    setTimeout(getData(tempArray[0], tempArray[1]), 5000);
  }
}
