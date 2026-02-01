import concurrent.futures
import threading
import os.path
import json
import tqdm
import tqdm.contrib
from typing import Callable
from api import api_local, CacheManager, CardApiRequest
from hint import CardRawData, CardRawDataItem


class TranslateHelper:
    # 某些日文不同卡名但中文翻译翻成同卡名的玩意
    special_card_name = {'礼品卡', '魔法神灯', '骷髅骑士', '混沌巫师', '暴风雨', '核心爆裂', '流星龙',
                         '宝贝龙', '磁力戒指', '补给部队', '扰乱怪衍生物', '契约履行'}

    FORCE_UPDATE_CARD_CACHE_ENABLE = False  # 强制更新卡片缓存
    FORCE_UPDATE_START_INDEX = 0  # 强制更新的起始cid

    def __init__(self, card_raw_data: CardRawData,
                 progress_update_cb: Callable[[str], None] = lambda _: None,
                 network_error_cb: Callable[[], None] = lambda: None,
                 dev_mode: bool = False):
        self.card_raw_data = card_raw_data
        self.progress_update_cb = progress_update_cb
        self.network_error_cb = network_error_cb
        self.dev_mode = dev_mode

        self._card_api = CardApiRequest()

        self.archived_data = None

        self._card_raw_data_length = len(self.card_raw_data)
        self._finished_progress_cnt = 0

        self._progress_lock = threading.Lock()
        self._progress_bar = None

        self._load_archived_data()

    def _load_archived_data(self):
        if self.dev_mode:
            with open(os.path.join("./unity/old_card_cache.json"), "r", encoding="utf8") as f:
                self.archived_data: CardRawData = json.load(f)

            self._progress_bar = tqdm.tqdm(total=len(self.card_raw_data), desc="Translating", disable=not self.dev_mode)

    def _add_progress_cnt(self):
        if self.dev_mode:
            self._progress_bar.update(1)

        with self._progress_lock:
            self._finished_progress_cnt += 1
            self.progress_update_cb(f"{self._finished_progress_cnt}/{self._card_raw_data_length}")

    def _is_force_update_card_cache(self, cid):
        if not self.FORCE_UPDATE_CARD_CACHE_ENABLE:
            return False
        if cid < self.FORCE_UPDATE_START_INDEX:
            return False
        return True

    def search_archived_data(self, cid: int, name_cn: str, desc_cn: str) -> CardRawDataItem | None:
        result_obj = None
        for data_obj in self.archived_data:
            if data_obj["name"]["zh-cn"] == name_cn:
                if name_cn not in self.special_card_name:
                    result_obj = data_obj
                    break
                if data_obj["desc"]["zh-cn"] == desc_cn:  # 某些特殊卡片要二次校验
                    result_obj = data_obj
                    break

        if self.dev_mode and result_obj is not None:
            CacheManager.add_cache(cid,
                                   jp_name=result_obj.get('name', {}).get('ja-jp', ''),
                                   cn_name=result_obj.get('name', {}).get('custom', ''),
                                   md_name=result_obj.get('name', {}).get('zh-cn', ''),
                                   original_desc=result_obj.get('desc', {}).get('zh-cn', ''),
                                   custom_desc=result_obj.get('desc', {}).get('custom', ''))
        return result_obj

    def card_translate(self) -> CardRawData:
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

        iterable = enumerate(self.card_raw_data)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(self.try_translate_single_card, item)
                for _, item in iterable
            ]

            for future in concurrent.futures.as_completed(futures):
                future.result()  # 捕获异常
                self._add_progress_cnt()

        if self.dev_mode:
            self._progress_bar.close()

        return self.card_raw_data

    def try_translate_single_card(self, item: CardRawDataItem):
        cid = item["cid"]
        name_md = item["name"]["zh-cn"]
        desc_md = item["desc"]["zh-cn"]

        force_update_card_cache = self._is_force_update_card_cache(cid)

        if force_update_card_cache:
            CacheManager.load_cache()

        # 新翻译文件(使用CID查找)
        if not force_update_card_cache and (result_api_local := api_local(cid)):
            # 在本地缓存中找到对应的日文名
            item["name"]["custom"] = result_api_local["name"]
            item["desc"]["custom"] = result_api_local["desc"]
            return item

        # 翻译API
        if result_api := self._card_api.api(name_md, cid, desc_md, self.network_error_cb, self.dev_mode):
            # print('API Remote Found:', name_md, result_api)

            # 在API中找到了对应的日文名
            item["name"]["custom"] = result_api["name"]
            item["desc"]["custom"] = result_api["desc"]
            return item

        # 旧版翻译文件
        if self.dev_mode and force_update_card_cache:
            if result_archived := self.search_archived_data(cid, name_md, desc_md):
                tqdm.tqdm.write(f'Local JSON Found: {name_md}')

                # 在已归档数据中找到了对应的日文名
                item["name"]["custom"] = result_archived["name"]["custom"]
                item["desc"]["custom"] = result_archived["desc"]["custom"]
                return item

        # 未找到对应的日文名
        if self.dev_mode:
            tqdm.tqdm.write(f"WARN: Can't find {name_md}({cid})")

        item["name"]["custom"] = item["name"]["zh-cn"]
        item["desc"]["custom"] = item["desc"]["zh-cn"]
        return item