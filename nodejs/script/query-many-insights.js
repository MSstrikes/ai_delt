let requestFacebook = require('request-facebook')
const logger = require('simple-json-logger')
const qs = require('querystring')
const {compose, withRetry, withRateLimit} = require('run-control')
const _ = require('lodash')
const get_config = require('./tool.js')
const config = get_config()

const queryString = process.argv[2]
const objectIds = _.slice(process.argv, 3)

requestFacebook = compose(
    withRetry({
        times: _.get(config, 'queryManyInsights.retryLimit', 3)
    }),
    withRateLimit(
        _.get(config, 'queryManyInsights.rateLimit', 100)
    ),
)(requestFacebook)

objectIds.forEach(objectId => {
    return requestFacebook({
        accessToken: config.accessToken,
        apiVersion: 'v2.12',
        path: `${objectId}/insights`,
        query: qs.parse(queryString)
    }).then(result => logger.info(result))
        .catch(err => logger.error(err))
})
