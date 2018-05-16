const _ = require('lodash')
const moment = require('moment-timezone')
const weighted = require('weighted')
const fs = require('fs')
const path = require('path')

let count = Number(process.argv[2])
if (!count) count = 1

console.log('loading builder...')
const builder = require('../builder')
console.log('builder loaded')

console.log(`building ${count} pts...`)
const pts = _.range(count).map(() => builder({_, moment, weighted}))
const ptsString = JSON.stringify(pts, null, 2)
console.log('pts built')

console.log('writing pts into file...')
fs.writeFileSync(path.resolve(__dirname, '../pts.json'), ptsString)
console.log('pts wrote into file')

console.log('build-pts succeeded!')