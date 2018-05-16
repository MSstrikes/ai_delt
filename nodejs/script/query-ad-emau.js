let requestFacebook = require('request-facebook')
const logger = require('simple-json-logger')
const qs = require('querystring')
const {compose, withRetry, withRateLimit} = require('run-control')
const _ = require('lodash')
const fs = require('fs');
const path = require('path')
const configFilepath = process.env.CONFIG_FILE_PATH
const config = require(path.resolve(configFilepath))

var pjson = JSON.parse(fs.readFileSync('../pts.json'))

requestFacebook = compose(
    withRetry({
        times: _.get(config, 'queryManyInsights.retryLimit', 3)
    }),
    withRateLimit(
        _.get(config, 'queryManyInsights.rateLimit', 100)
    ),
)(requestFacebook)

pjson.forEach(pt => {
    return requestFacebook({
        accessToken: config.accessToken,
        apiVersion: 'v2.12',
        path: config.adAccountId + '/delivery_estimate',
        query: {
            targeting_spec: pt['adset_spec']['targeting'],
            optimization_goal: pt['adset_spec']['optimization_goal']
        }
    }).then(result => {
        logger.info({result, pt})
    })
        .catch(err => logger.error(err))
})
