import asyncio

# simple_work
# ctx คือ context ของ worker ส่วน job_data คือข้อมูลที่เราจะส่งเข้ามา
async def simple_work(ctx, job_data: str):
    print(f" [Worker] starting: {job_data}")
    await asyncio.sleep(2) # จำลองการใช้เวลาทำงาน 2 วินาที
    print(f"[Worker] completed ")
    return f"Success: {job_data}"

# กำหนดค่า WorkerSettings เพื่อบอกให้ ARQ รู้จักฟังก์ชันนี้
class WorkerSettings:
    functions = [simple_work]