# Update
使用串口及开发板的U-boot完成对开发板上OpenWrt固件的自动升级。

## 说明
将开发板处于正常的LEDE系统状态下。

执行`update.py`

## 规划
1. 串口可配置，读取循环
2. 识别特定字符串，写入对应指令
3. 自动识别串口
4. 自动重传