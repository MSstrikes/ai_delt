module.exports = function ({_, moment, weighted}) {
    // ------------------------------------函数定义----------------------------------------
    function pickupN(n, items) {
        if (n > items.length) throw new Error('n cannot be greater than items.length')
        // 对数组进行随机打乱,
        // return大于0则交换位置,小于等于0就不交换
        // 由于Math.random()产生的数字为0-1之间的数
        // 所以0.5-Math.random()的是否大于0是随机结果
        // 进而实现数组的随机打乱
        var array = items.slice()
        array.sort(function () {
            return 0.5 - Math.random()
        })
        // 在控制台输出结果
        return array.splice(0, n)
    }

    function randomFrom(lowerValue, upperValue) {
        return Math.floor(Math.random() * (upperValue - lowerValue + 1) + lowerValue);
    }

    const dollarToCent = x => x * 100
    const randomTrueFalse = (trueWeight = 1, falseWeight = 1) => weighted([true, false], [trueWeight, falseWeight])
    const cleanArray = x => {
        const array = _.chain(x).compact().uniq().value()
        return array.length > 0 ? array : undefined
    }

    function get_behavoirs(behavoir_set, countries) {
        var out = []
        behavoir_set.forEach(x => {
            if (x['country'] == undefined) {
                out = out.concat(x)
            } else {
                countries.forEach(y => {
                    if (y == x['country']) {
                        out = out.concat({'id': x['id'], 'name': x['name']})
                    }
                })
            }
        })
        return out
    }

    // ------------------------------------常量声明----------------------------------------
    const _game = 'BA'
    const _os = weighted(['Android', 'iOS'], [0.5, 0.5])
    const _ios_version = weighted(['6.0', '7.0', '8.0', '9.0'])//'2.0', '3.0', '4.0', '4.3', '5.0',
    const _android_version = weighted(['5.0', '6.0', '7.0', '8.0'])//'2.0', '2.1', '2.2', '2.3', '3.0', '3.1', '3.2', '4.0', '4.1', '4.2', '4.3', '4.4',
    //images-hash
    const imageHash = weighted(`{python::get_image_hash}`)
    // data
    const _devices = `{python::get_devices}`
    const object_store_url = {
        'Android': 'http://play.google.com/store/apps/details?id=com.tap4fun.brutalage_test',
        'iOS': 'https://itunes.apple.com/app/id1156787368'
    }[_os]
    const _creatives = {
        'en': weighted(`{python::get_creative('en')}`),
        'fr': weighted([1]),
        'de': weighted([1]),
        'zh': weighted([1])
    }
    // const _customAudience = {
    //     '美国': weighted(`{python::get_audience()}`),
    //     'T1 英语':weighted([1]),
    //     'T1 法语': weighted([1]),
    //     'T1 德语': weighted([1]),
    //     'T1 中文': weighted([1]),
    //     'ROW': weighted([1]),
    //     '欧盟 英语': weighted([1])
    // }
    // controls
    const _location = weighted([
        '美国'//,
        //'T1 英语',
        //'T1 法语',
        //'T1 德语',
        //'T1 中文',
        //'ROW',
        //'欧盟 英语'
    ])
    // fields
    const myDate = new Date();
    const _platformFacebookFeed = randomTrueFalse(3, 1)
    const _platformFacebookSuggestedVideo = _platformFacebookFeed && randomTrueFalse()
    const _platformInstagramStream = !_platformFacebookFeed || randomTrueFalse() // all other positions rely on facebook feed. so if facebook feed is disabled, the only instagram position must be selected
    const _platformAudienceNetworkClassic = _platformFacebookFeed && randomTrueFalse()
    const _platformAudienceNetworkRewardedVideo = _platformFacebookFeed && randomTrueFalse()
    const optimizationGoal = 'OFFSITE_CONVERSIONS' //weighted(['APP_INSTALLS', 'OFFSITE_CONVERSIONS'],[0.4, 0.6])
    const status = 'ACTIVE'
    const dailyBudget = dollarToCent(500)
    const billingEvent = 'IMPRESSIONS'
    const objective = 'APP_INSTALLS'
    const buyingType = 'AUCTION'
    const _targeting_pool = ['BHV']//'interest','behavoir','coordinate'
    const _targeting_type = pickupN(randomFrom(1, _targeting_pool.length), _targeting_pool).sort()
    const minAge = randomFrom(13, 25)
    const maxAge = randomFrom(40, 65)
    const appInstallState = 'not_installed'
    const genders = weighted([[1, 2], [1], [2]])
    const wifi_setting = weighted([["Wifi"], undefined])
    const locationTypes = weighted([['home', 'recent'], ['travel_in']])
    const publisherPlatforms = cleanArray([
        _platformFacebookFeed && 'facebook',
        _platformFacebookSuggestedVideo && 'facebook',
        _platformInstagramStream && 'instagram',
        _platformAudienceNetworkClassic && 'audience_network',
        _platformAudienceNetworkRewardedVideo && 'audience_network'
    ])
    const facebookPositions = cleanArray([
        _platformFacebookFeed && 'feed',
        _platformFacebookSuggestedVideo && 'suggested_video'
    ])
    const instagramPositions = cleanArray([
        _platformInstagramStream && 'stream',
    ])
    const audienceNetworkPositions = cleanArray([
        _platformAudienceNetworkClassic && 'classic',
        _platformAudienceNetworkRewardedVideo && 'rewarded_video'
    ])
    const excludedPublisherCategories = ['debated_social_issues', 'tragedy_and_conflict']
    const _behavoir = `{python::get_behavoirs}`
    //-------------------------------------依赖配置----------------------------------
    const _language = {
        '美国': 'en',
        'T1 英语': 'en',
        'T1 法语': 'fr',
        'T1 德语': 'de',
        'T1 中文': 'zh',
        'ROW': 'en',
        '欧盟 英语': 'en'
    }[_location]
    const countryGroups = {
        'ROW': ['android_paid_store'],
        '欧盟 英语': ['eea']
    }[_location]
    const countries = {
        '美国': ['US'],
        'T1 英语': ['CA', 'SG', 'GB', 'AU'],
        'T1 法语': ['LU', 'FR'],
        'T1 德语': ['SE', 'CH', 'DK', 'DE'],
        'T1 中文': ['HK', 'TW']
    }[_location]

    const excludedGeoLocations = {
        'ROW': {
            'countries': [
                'PK', 'IN'
            ],
            'location_types': [
                'home'
            ]
        }
    }[_location]
    short_names = {
        'Android': 'ADR',
        'iOS': 'IOS',
        '美国': 'US'
    }
    const name = `${myDate.getDate()}-${myDate.getMonth() + 1} ${_game} ${short_names[_os]} ${short_names[_location]} ${_targeting_type.join("+")} ${moment().tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss')} [youhaolin]`
    const attributionSpec = {
        'APP_INSTALLS': undefined,
        'OFFSITE_CONVERSIONS': [{'event_type': 'CLICK_THROUGH', 'window_days': 7}]
    }[optimizationGoal]
    const promotedObject = {
        'APP_INSTALLS': {
            'application_id': '634204786734953',
            'object_store_url': object_store_url
        },
        'OFFSITE_CONVERSIONS': {
            'application_id': '634204786734953',
            'object_store_url': object_store_url,
            'custom_event_type': 'PURCHASE'
        }
    }[optimizationGoal]
    const _custom_behavoir = get_behavoirs(_behavoir, countries)

    function get_targeting(ttype, object) {
        var i = 0
        const len = _targeting_type.length
        for (; i < len; ++i) {
            if (_targeting_type[i] == ttype) {
                return object
            }

        }
    }

    const behaviors = get_targeting('BHV', pickupN(randomFrom(1, _custom_behavoir.length), _custom_behavoir))
    // const customAudiences = get_targeting('audience',_customAudience[_location])
    const userOs = {
        'Android': ['Android_ver_' + _android_version + '_and_above'],
        'iOS': ['iOS_ver_' + _ios_version + '_and_above']
    }[_os]
    const userDevice = {
        'Android': pickupN(randomFrom(1, _devices['Android'].length), _devices['Android']),
        'iOS': pickupN(randomFrom(1, _devices['iOS'].length), _devices['iOS'])
    }[_os]
    const creative = _creatives[_language]
    const bid_amount = {
        'APP_INSTALLS': dollarToCent(3),
        'OFFSITE_CONVERSIONS': dollarToCent(100)
    }[optimizationGoal]
    const bid_strategy = weighted(['LOWEST_COST_WITH_BID_CAP', 'TARGET_COST'], [0.5, 0.5])

    return {
        name: name,
        status: status,
        adset_spec: {
            name: name,
            status: status,
            daily_budget: dailyBudget,
            bid_amount: bid_amount,
            bid_strategy: bid_strategy,
            billing_event: billingEvent,
            attribution_spec: attributionSpec,
            campaign_spec: {
                name: name,
                status: status,
                objective: objective,
                buying_type: buyingType
            },
            optimization_goal: optimizationGoal,
            promoted_object: promotedObject,
            targeting: {
                age_max: maxAge,
                age_min: minAge,
                app_install_state: appInstallState,
                excluded_connections: [{'id': 634204786734953}],
                behaviors: behaviors,
                genders: genders,
                device_platforms: ["mobile"],
                geo_locations: {
                    countries: countries,
                    country_groups: countryGroups,
                    location_types: locationTypes
                },
                excluded_publisher_categories: excludedPublisherCategories,
                // custom_audiences: customAudiences,
                excluded_geo_locations: excludedGeoLocations,
                publisher_platforms: publisherPlatforms,
                facebook_positions: facebookPositions,
                instagram_positions: instagramPositions,
                audience_network_positions: audienceNetworkPositions,
                user_os: userOs,
                user_device: userDevice,
                wireless_carrier: wifi_setting
            }
        },
        creative: creative
    }
}
