import asyncio
from arq import create_pool
from arq.connections import RedisSettings

async def main():
    # สร้างการเชื่อมต่อไปที่ Redis
    redis = await create_pool(RedisSettings())
    
    # ส่งงานเข้าคิว ชื่อฟังก์ชัน 'simple_work' และส่งข้อมูล 'Test Job 01' ไปให้
    job_data = "Test Job 01"
    print(f"[Client] กำลังส่งงาน '{job_data}' เข้าคิว...")
    await redis.enqueue_job('simple_work', job_data)
    print("ส่งงานสำเร็จ!")

if __name__ == '__main__':
    asyncio.run(main())