let requestFacebook = require('request-facebook')
const {inspect} = require('util')
const {compose, withRetry, withRateLimit} = require('run-control')
const _ = require('lodash')
const get_config = require('./tool.js')
const config = get_config()

console.log('loading pts...')
const pts = require('../pts')
console.log('pts loaded')

requestFacebook = compose(
    withRetry({
        times: _.get(config, 'createAds.retryLimit', 3)
    }),
    withRateLimit(
        _.get(config, 'createAds.rateLimit', 100)
    ),
)(requestFacebook)

let count = 0

console.log(`creating ${pts.length} ads...`)
Promise.all(pts.map(async (pt, index) => {
    try {
        const ad = await requestFacebook({
            accessToken: config.accessToken,
            apiVersion: 'v3.0',
            method: 'POST',
            path: `${config.adAccountId}/ads`,
            body: pt
        })
        count++
        console.log(`succeeded to created ${index + 1}th ad: ${ad.id}`)
    } catch (err) {
        err = err.response ? err.response.body : err
        console.error(`failed to to create ${index + 1}th ad`, inspect(err, false, null))
    }
}))
    .then(() => {
        console.log(`${count}/${pts.length} ads created`)
    })
