# 探索性分析 Notebooks

此目录用于存放 Jupyter Notebook，用于：
- 数据探索与可视化
- 特征分布分析
- 模型调参实验
- 结果展示

## 命名规范

- `01_data_exploration.ipynb`：数据探索
- `02_feature_analysis.ipynb`：特征分析
- `03_model_experiment.ipynb`：模型实验
- `04_results_visualization.ipynb`：结果可视化

## 运行前准备

```bash
# 确保已安装依赖
pip install -r ../requirements.txt

# 启动 Jupyter
jupyter notebook
```

## 注意

- Notebooks 中不要包含大文件输出（图片除外）
- 清理输出后再提交（`Kernel > Restart & Clear Output`）
- 关键发现记录到 `docs/` 目录
