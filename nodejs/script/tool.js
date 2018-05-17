const parse_config = function (uri, encoding) {
    const fs = require('fs')
    const file_encoding = encoding == null ? 'UTF-8' : encoding  //定义编码类型
    let keyvalue = {}  //存储键值对
    try {
        const content = fs.readFileSync(uri, file_encoding)
        const regexjing = /\s*(#+)/  //去除注释行的正则
        const regexkong = /\s*=\s*/  //去除=号前后的空格的正则


        let arr_case = null
        const regexline = /.+/g  //匹配换行符以外的所有字符的正则
        while (arr_case = regexline.exec(content)) {  //过滤掉空行
            if (!regexjing.test(arr_case)) {  //去除注释行
                keyvalue[arr_case.toString().split(regexkong)[0]] = arr_case.toString().split(regexkong)[1]  //存储键值对
            }
        }
    } catch (e) {
        //e.message  //这里根据自己的需求返回
        return null
    }
    return keyvalue
}

const get_config = function () {
    const tmp = parse_config(process.env.CONFIG_FILE_PATH, "utf-8")
    return {
        "adAccountId": `act_${tmp['account_id']}`,
        "accessToken": tmp['access_token'],
        "createAds": {
            "retryLimit": tmp['createAds_retryLimit'],
            "rateLimit": tmp['createAds_rateLimit']
        },
        "queryManyInsights": {
            "retryLimit": tmp['queryManyInsights_retryLimit'],
            "rateLimit": tmp['queryManyInsights_rateLimit']
        }
    }
}

module.exports = get_config
