
# mandelbrotアート生成
import random
seed = 5720
print(f"Generating mandelbrot art with seed {seed}")

# アート生成ロジック（簡略版）
for i in range(10):
    x = random.random() * 100
    y = random.random() * 100
    print(f"  Point {i}: ({x:.2f}, {y:.2f})")

print("Art generation complete!")
