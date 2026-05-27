# 花瓣网画板下载器

一个简单易用的花瓣网画板图片批量下载工具，支持从 CSV 批量读取画板 ID 并下载。

> 炼丹收集素材太费事了，好吧，这个就是为了给炼丹收集素材提效的

## 功能特点

- 支持从 CSV 读取画板 ID 列表
- 支持命令行批量下载
- 自动读取本地 Cookie 文件
- 自动保存原始图片质量
- 使用图片描述作为文件名

## 安装说明

1. 确保已安装 Python 3.11 版本
2. 克隆或下载本项目
3. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 准备两个文件：
   - **CSV**：存放画板 ID 列表，支持 `id` 或 `board_id` 列
   - **Cookie 文件**：保存浏览器里复制的 Cookie 字符串

2. 运行命令：
```bash
python main.py --cookie-path ./COOKIE boards.csv
```

3. 下载结果会保存到 `huohuab/{花瓣 id}/`

4. 如果 CSV 里有自定义的 ID 列名，可以加 `--id-column`：
```bash
python main.py --cookie-path ./COOKIE --id-column boardId boards.csv
```

## CSV 格式

支持两种格式：

```csv
id
94146939
12345678
```

或者：

```csv
board_id,title
94146939,素材收集
12345678,配色参考
```

如果 CSV 没有表头，会默认读取第一列作为画板 ID。

## 文件说明

- `main.py`: 命令行入口，读取 CSV 并批量下载
- `downloader.py`: 下载核心逻辑
- `huohuab/`: 默认的图片保存目录

## 注意事项

1. 需要登录花瓣网并获取有效的 Cookie
2. 下载速度受网络条件和图片数量影响
3. 保存路径如果不存在会自动创建
4. 重复运行时会跳过已下载的图片

## 常见问题

1. **下载失败**
   - 检查 Cookie 是否有效
   - 确认网络连接正常

2. **CSV 读取失败**
   - 检查是否存在 `id` 或 `board_id` 列
   - 如果列名不同，使用 `--id-column` 指定

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

感谢花瓣网提供的图片资源，使用请按照版权的要求。
