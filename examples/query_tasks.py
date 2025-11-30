"""飞书任务查询示例

本示例演示如何使用 larkpy 库查询飞书任务。

使用前请确保：
1. 在飞书开放平台创建应用并获取 app_id 和 app_secret
2. 为应用申请以下权限之一：
   - task:task:readonly（查看任务）
   - task:task（查看、创建、编辑和删除任务）
"""

from larkpy import LarkTask
import time

# 初始化 Task API（请替换为你的实际凭证）
task_api = LarkTask(
    app_id='your_app_id',
    app_secret='your_app_secret'
)

# ============================================
# 示例 1: 查询已完成的任务（自动使用 v2 API）
# ============================================
print("=" * 50)
print("示例 1: 查询已完成的任务")
print("=" * 50)

result = task_api.list_tasks(completed=True, page_size=10)

if result['code'] == 0:
    tasks = result['data']['items']
    print(f"找到 {len(tasks)} 个已完成的任务：\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.get('summary', '无标题')}")
        if 'completed_at' in task:
            # completed_at 是毫秒时间戳
            completed_time = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(task['completed_at'] / 1000)
            )
            print(f"   完成时间: {completed_time}")
        print()
    
    # 处理分页
    if result['data'].get('has_more'):
        print("还有更多任务，可以使用 page_token 获取下一页")
        print(f"page_token: {result['data']['page_token']}")
else:
    print(f"查询失败: {result['msg']}")

# ============================================
# 示例 2: 查询最近7天内已完成的任务（自动使用 v1 API）
# ============================================
print("\n" + "=" * 50)
print("示例 2: 查询最近7天内已完成的任务")
print("=" * 50)

# 计算时间戳（毫秒）
current_time = int(time.time() * 1000)
seven_days_ago = current_time - (7 * 24 * 60 * 60 * 1000)

result = task_api.list_tasks(
    completed=True,
    start_create_time=str(seven_days_ago),
    end_create_time=str(current_time),
    page_size=10
)

if result['code'] == 0:
    tasks = result['data']['items']
    print(f"找到 {len(tasks)} 个最近7天内已完成的任务：\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.get('summary', '无标题')}")
        
        # 显示创建时间
        if 'created_at' in task:
            created_time = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(int(task['created_at']) / 1000)
            )
            print(f"   创建时间: {created_time}")
        
        # 显示完成时间
        if 'completed_at' in task:
            completed_time = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(int(task['completed_at']) / 1000)
            )
            print(f"   完成时间: {completed_time}")
        print()
else:
    print(f"查询失败: {result['msg']}")

# ============================================
# 示例 3: 查询所有未完成的任务（自动使用 v2 API）
# ============================================
print("\n" + "=" * 50)
print("示例 3: 查询所有未完成的任务")
print("=" * 50)

result = task_api.list_tasks(completed=False, page_size=10)

if result['code'] == 0:
    tasks = result['data']['items']
    print(f"找到 {len(tasks)} 个未完成的任务：\n")
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.get('summary', '无标题')}")
        
        # 显示截止时间（如果有）
        if 'due' in task and task['due'].get('timestamp'):
            due_time = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(int(task['due']['timestamp']) / 1000)
            )
            print(f"   截止时间: {due_time}")
        print()
else:
    print(f"查询失败: {result['msg']}")

# ============================================
# 示例 4: 查询某个时间点之后创建的所有任务（自动使用 v1 API）
# ============================================
print("\n" + "=" * 50)
print("示例 4: 查询30天内创建的所有任务")
print("=" * 50)

thirty_days_ago = current_time - (30 * 24 * 60 * 60 * 1000)

result = task_api.list_tasks(
    start_create_time=str(thirty_days_ago),
    page_size=10
)

if result['code'] == 0:
    tasks = result['data']['items']
    print(f"找到 {len(tasks)} 个30天内创建的任务：\n")
    
    completed_count = sum(1 for task in tasks if task.get('completed_at'))
    uncompleted_count = len(tasks) - completed_count
    
    print(f"已完成: {completed_count} 个")
    print(f"未完成: {uncompleted_count} 个\n")
    
    for i, task in enumerate(tasks, 1):
        status = "✓" if task.get('completed_at') else "○"
        print(f"{status} {i}. {task.get('summary', '无标题')}")
else:
    print(f"查询失败: {result['msg']}")

# ============================================
# 示例 5: 分页查询示例
# ============================================
print("\n" + "=" * 50)
print("示例 5: 分页查询所有任务")
print("=" * 50)

all_tasks = []
page_token = None
page_count = 0

while True:
    result = task_api.list_tasks(
        page_size=20,
        page_token=page_token
    )
    
    if result['code'] == 0:
        page_count += 1
        tasks = result['data']['items']
        all_tasks.extend(tasks)
        
        print(f"第 {page_count} 页: 获取到 {len(tasks)} 个任务")
        
        # 检查是否还有更多数据
        if result['data'].get('has_more'):
            page_token = result['data']['page_token']
        else:
            break
    else:
        print(f"查询失败: {result['msg']}")
        break

print(f"\n总共获取到 {len(all_tasks)} 个任务")

print("\n" + "=" * 50)
print("示例完成")
print("=" * 50)
