from typing import Callable

from tqdm import tqdm
from tqdm.contrib import tenumerate

from api import api, api_local, CacheManager
from hint import CardRawData, CardRawDataItem


def card_translate(
    archived_Data: CardRawData,
    card_raw_data: CardRawData,
    progress_update_cb: Callable[[str], None] = lambda _: None,
    network_error_cb: Callable[[], None] = lambda: None,
    dev_mode: bool = False,
) -> CardRawData:

    FORCE_UPDATE_CARD_CACHE = False  # 强制更新卡片缓存

    # 统计同名卡的函数
    # card_name = {}
    # def stat_repeat_card_name(name_md: str, desc_md: str):
    #     if name_md not in card_name:
    #         card_name[name_md] = desc_md
    #     elif desc_md == card_name[name_md]:
    #         pass
    #     else:
    #         success = 0
    #         for x in archived_Data:
    #             if x["name"]["zh-cn"] == name_md:
    #                 if x["desc"]["zh-cn"] == desc_md:
    #                     success += 1
    #                 elif x["desc"]["zh-cn"] == card_name[name_md]:
    #                     success += 1
    #
    #                 if success >= 2:
    #                     print('Need Add to list:', name_md)
    #                     break
    #
    #         if success < 2:
    #             print('Error:', name_md, "\n", desc_md, "\n", card_name[name_md])
    #             print('')

    # 某些日文不同卡名但中文翻译翻成同卡名的玩意
    special_card_name = {'礼品卡', '魔法神灯', '骷髅骑士', '混沌巫师', '暴风雨', '核心爆裂', '流星龙',
                         '宝贝龙', '磁力戒指', '补给部队', '扰乱怪衍生物', '契约履行'}

    def search_archived_data(name_cn: str, desc_cn: str) -> CardRawDataItem | None:
        result_obj = None
        for data_obj in archived_Data:
            if data_obj["name"]["zh-cn"] == name_cn:
                if name_cn not in special_card_name:
                    result_obj = data_obj
                    break
                if data_obj["desc"]["zh-cn"] == desc_cn:  # 某些特殊卡片要二次校验
                    result_obj = data_obj
                    break

        if dev_mode and result_obj is not None:
            CacheManager.add_cache(cid,
                                   jp_name=result_obj.get('name', {}).get('ja-jp', ''),
                                   cn_name=result_obj.get('name', {}).get('custom', ''),
                                   md_name=result_obj.get('name', {}).get('zh-cn', ''),
                                   original_desc=result_obj.get('desc', {}).get('zh-cn', ''),
                                   custom_desc=result_obj.get('desc', {}).get('custom', ''))
        return result_obj

    iterable = (
        tenumerate(card_raw_data)
        if dev_mode
        else enumerate(card_raw_data)
    )

    for i, item in iterable:
        cid = item["cid"]
        name_md = item["name"]["zh-cn"]
        desc_md = item["desc"]["zh-cn"]

        progress_update_cb(f"{i}/{len(card_raw_data)}")

        if FORCE_UPDATE_CARD_CACHE:
            CacheManager.load_cache()

        # 新翻译文件(使用CID查找)
        if (result_api_local := api_local(cid)) and not FORCE_UPDATE_CARD_CACHE:
            # 在本地缓存中找到对应的日文名
            item["name"]["custom"] = result_api_local["name"]
            item["desc"]["custom"] = result_api_local["desc"]
            continue

        # 翻译API
        if result_api := api(name_md, cid, desc_md, network_error_cb, dev_mode):
            # print('API Remote Found:', name_md, result_api)

            # 在API中找到了对应的日文名
            item["name"]["custom"] = result_api["name"]
            item["desc"]["custom"] = result_api["desc"]
            continue

        # 旧版翻译文件
        # if result_archived := search_archived_data(name_md, desc_md):
        #     # print('Local JSON Found:', name_md)
        #
        #     # 在已归档数据中找到了对应的日文名
        #     item["name"]["custom"] = result_archived["name"]["custom"]
        #     item["desc"]["custom"] = unity(result_archived["desc"]["custom"])
        #     continue

        # 未找到对应的日文名
        if dev_mode:
            tqdm.write(f"WARN: Can't find {name_md}({cid})")

        item["name"]["custom"] = item["name"]["zh-cn"]
        item["desc"]["custom"] = item["desc"]["zh-cn"]

    return card_raw_data
