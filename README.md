# DHelper

这是一个医疗影像分析工具，使用多代理系统分析影像数据。

## 环境要求

- Python 3.12 或更高版本
- Conda（用于管理虚拟环境）

## 安装步骤

### 1. 创建新的 Conda 虚拟环境

打开终端，运行以下命令创建一个新的 Conda 虚拟环境（建议使用 Python 3.12）：

```bash
conda create -n dhelper python=3.12 -y
```

- `dhelper` 是环境名称，你可以根据需要修改。
- `python=3.12` 指定 Python 版本，你可以根据项目需求调整。

### 2. 激活虚拟环境

创建环境后，激活它：

```bash
conda activate dhelper
```

激活后，你的终端提示符会显示 `(dhelper)`，表示环境已激活。

### 3. 安装项目依赖

确保项目目录中有 `requirements.txt` 文件（如果没有，请创建或从项目中获取）。然后安装依赖：

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，你可以手动安装主要依赖（基于项目代码）：

```bash
pip install pandas langchain langchain-core
```

### 4. 配置项目

项目需要配置文件：
- `config/config.ini`
- `config/config_llm.ini`

请确保这些文件存在并正确配置（包含必要的 API 密钥等）。

### 5. 运行项目

激活环境后，运行主程序：

```bash
python main.py
```

程序会提示输入影像号，然后进行分析并保存结果。

## 注意事项

- 确保数据文件 `data/Thymus_data.csv` 存在。
- 如果遇到权限问题，使用 `sudo`（仅限 macOS/Linux）。
- 要退出环境，使用 `conda deactivate`。

## 故障排除

- 如果 conda 命令未找到，确保已安装 Miniconda 或 Anaconda。
- 如果 pip 安装失败，检查网络连接或使用国内镜像源。

## 贡献

欢迎提交 issue 和 pull request。