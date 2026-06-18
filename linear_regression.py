import numpy as np
import matplotlib.pyplot as plt

# 生成数据
np.random.seed(42)
x = np.linspace(0, 10, 100)
y = 3 * x + 7 + np.random.randn(100) * 2  # y = 3x + 7 + 噪声

# 初始化参数
w = np.random.randn()
b = np.random.randn()
lr = 0.01  # 学习率
epochs = 1000  # 训练轮数

# 梯度下降训练
for epoch in range(epochs):
    # 预测值
    y_pred = w * x + b

    # 均方误差损失
    loss = np.mean((y_pred - y) ** 2)

    # 计算梯度
    dw = 2 * np.mean((y_pred - y) * x)
    db = 2 * np.mean(y_pred - y)

    # 更新参数
    w = w - lr * dw
    b = b - lr * db

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss:.4f}')

print(f'Trained Model: y = {w:.2f}x + {b:.2f}')

# 可视化结果
plt.scatter(x, y, label='Data')
plt.plot(x, w * x + b, 'r', label='Fitted Line')
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.title("CQUPT2024211877", loc="center")
plt.savefig("linear_regression_result.png", dpi=150)
plt.show()
