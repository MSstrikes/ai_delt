from ptbuilder import mysql


def get_image_hash():
    return ["f9841c0db9abdb641d986483adbfaea2",
            "f85cc623559ffd67dd19b04936e313ee",
            "f16a07d467e231c167cb207ee9404c0b",
            "f0db137c6a903d4603127a990e31fc29",
            "ea5bd76d733ce0b1c9a5b5a925cf8969",
            "e95b33dbd1254e865942f3e1fdad68f4",
            "e893ede9f32f57ce45aa557f9b8eab54",
            "d9e77443ee77acaaf0d48c33dfa55b5c",
            "d6b75cbd179651b79a8e85cc291b9eff",
            "d529253790a8f4d1f7d7c17c4e04c992",
            "d2ef2225a127c69bf8a0c6d6ebc926aa",
            "cb9ac8919498a68d061a5e15444a48f4",
            "ca2db2c90cac046b27179fb06241b5ba",
            "c9d1bca232371d789fe1613d7b52478b",
            "c9c079403494f1760529c91f0cea14b0",
            "c90cca2802b3e605dc26ee58ad75b498",
            "b30cfae9be3b3e524fbf07eae0349d61",
            "b27a9c78716ff8f07d296138c233ccfc",
            "ad3274468c4bd5bb6e9d5cb738fe5d0c",
            "acde67e6a6419cd4e7d096f9dd60bbf8",
            "96b06ab353ed3cdba7547bc2f16c6491",
            "8ede1373aa1c73f927892241691bbcd5",
            "8b5edf996b3699630ed60f933d4b482f",
            "8a7ffcb162e577875822e9c465531452",
            "8221833ad062ad0032fcb8be538a2051",
            "7c5ee7098e83c7f61400e8b197ca3562",
            "777f1ee738f551a3c42c128ac7e9144d",
            "75242e54f1d795ad5964f087e54fe40d",
            "72d21250700699f3f735bcdcb8b329d6",
            "6869b274e92c0357c6624f5c4c58bb83",
            "6650708cb2edf176469dab653bb4c2c3",
            "60ec2ad210b1e6f475abb9d83a6c113f",
            "5dc6b08f14dab1977b5e9c43fed1471f",
            "5c8a7e87bfa9143b6f21f7531eff9dc4",
            "5b56b28779fe565ba69adc03cebfd89c",
            "57c2e81b8a3171f26ae2a11709aa417f",
            "5026b464b9587d749fd740e36db35f85",
            "4fb3c1a041cd7864bc3416ccc802b6b0",
            "4de32e2e07264057766a47f4ed694686",
            "4dcbf5c0eb866f778dce8e95f7765d17",
            "44103f6480cec54425cc391ecd1dfebd",
            "41a0720dd7f0fabd3642a821a96b9472",
            "40da17f299ce4b321a43c9cf121ae1ee",
            "3bfe3e0022f31731562a66225e07d75b",
            "343cfb00f9f5d0c709dfa05ee4117d14",
            "2b1bbc3b72f2300fb6c9385ace98d966",
            "2ac32c77086d10cc536d7d686ee98bab",
            "29fe34d8e0e53c59966829f5505ef735",
            "286eae80b9b3d81345443fda203e0b8c",
            "223f496ab22ead101f7f9c96ac7f90f8",
            "1a1db32d4fe22408551f19d375cd9a59",
            "19968f869ab85a23269efee9fcffaf7e",
            "1749c55306617229c530c4ba02f43c52",
            "14ee80be9727a523385992b87793598d",
            "12fcb26b3752951ba8a9cd152f903a64",
            "0fe408a9c185e7e1e2cb8c86f3c507b9",
            "0e7b9cb86f8490f89cc2ca1563c53528",
            "0d7c901d84766044f83d1b630655bd58",
            "0ae0c8f44eaa5125aa42aef0c2e43c79",
            "071d9539bf9dbf197d12a0bb28042061",
            "0203fd8bbdb9d90c425479a27568378c",
            "67fef84b319c912819ae8b61afb533cb",
            "549d40639293585abe90cb10fd231ec5",
            "5a602c805635e42893e30766134439e6",
            "ec4635b50537d69d5b2c99b78817b32c",
            "49b42a0822460ef005840672123d18be",
            "62c116c031eb99dadc17c23941d3fc6c",
            "73d7b3cccf70f6795618fb9ef7f2cc22",
            "6d2f01171d3087099ad19f4e9c1b8575",
            "e8362158f6211ff69a0c5a7c959c5bcf",
            "1dc835ef5711792a90e507b91f063919",
            "73597029121683f3590cd697d73ad316",
            "f398671090b16589ce446c41514ff363",
            "b195b102fca457cb50899d959da35bb2",
            "73cc6febd2045c022b57b99f889cee94",
            "c8b0a2ba44b94f089dcf775543b281ff",
            "659810ed7f804b1db9923b4704fadc13",
            "63aa76cce8ac8edeeb28dc8b4d66d964",
            "3e0d97781ae931ed7141dfc900e245f2",
            "4a306f037e87424bfa38b21ae92d02c9"]


def get_devices():
    out = mysql.get_table('dw_dim_device')
    android_array = []
    ios_array = []
    for row in out:
        if row[2] == 'iOS':
            ios_array.append(row[1])
        if row[2] == 'Android':
            android_array.append(row[1])
    out_dict = dict()
    out_dict['iOS'] = ios_array
    out_dict['Android'] = android_array
    return out_dict


def get_creative(language):
    # 使用{)(}符号标记
    imageHash = '{)(}imageHash{)(}'
    object_store_url = '{)(}object_store_url{)(}'
    out = mysql.get_table('dw_dim_creative')
    json_out = []
    for row in out:
        if row[2] == language:
            for message in row[4:len(row)]:
                if len(message) > 10:
                    json_out.append({
                        'object_story_spec': {
                            'page_id': '1643949305846284',
                            'video_data': {
                                'video_id': str(row[3]),
                                'message': message,
                                'call_to_action': {
                                    'type': 'INSTALL_NOW',
                                    'value': {
                                        'application': '634204786734953',
                                        'link': object_store_url
                                    }
                                },
                                'image_hash': imageHash
                            }
                        }
                    })
    return json_out


def get_behavoirs():
    out = mysql.get_table('dw_dim_behavior')
    behavoir_set = []
    for row in out:
        if row[3] == '':
            behavoir_set.append({'id': str(row[1]), 'name': row[2]})
        else:
            behavoir_set.append({'id': str(row[1]), 'name': row[2], 'country': row[3]})
    return behavoir_set
