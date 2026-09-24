# DSTModLoader

针对用户提供的 Don't Starve Together iOS arm64 可执行文件的本地模组目录辅助工程。

## 功能

1. dylib 被加载时自动创建：
   `Documents/DoNotStarveTogether/mods/`
2. 不使用固定 UUID，而是通过 iOS `NSDocumentDirectory` 获取当前 App 容器，因此重新安装/重签后容器 UUID 改变也不会失效。
3. 用户将**已经解压**的 DST 模组目录放进 `mods/` 后，由 DST 原有的 `ModIndex/ModWrangler` 读取。
4. Lua 修改把 `MODS_ENABLED` 从 false 改为 true。
5. Redux 主菜单增加：
   `物品收藏/玩家摘要 → 模组 → 资料 → 选项`
   其中文字沿用游戏已有 `STRINGS.UI.*`。
6. 存档内暂停菜单增加“模组”入口，复用游戏已有 `ModsScreen`。

## 构建

需要 macOS + Xcode/iPhoneOS SDK + Theos。

    export THEOS=/path/to/theos
    make clean
    make

产物为 `.theos/obj/debug/DSTModLoader.dylib`。

## 接入主程序

用户提供的主程序是 arm64 Mach-O。项目同时提供 `patch_load_dylib.py`，
用于在现有 Mach-O 的 load commands 空间中增加：

    @executable_path/Frameworks/DSTModLoader.dylib

注意：修改 Mach-O 后原有 Apple code signature 会失效，需要使用你自己的合法签名流程重新签名。
