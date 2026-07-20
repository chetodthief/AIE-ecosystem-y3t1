import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from label_studio_sdk import LabelStudio

def main():
    print("=== Testing Label Studio Connection ===")
    
    # 1. Check if the API key is still the default placeholder
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA5MTcxNzE3MCwiaWF0IjoxNzg0NTE3MTcwLCJqdGkiOiJhZGI4MjY5ODA1Nzc0OTc1OTNkOTU2NWFiYzQ0NTdhMyIsInVzZXJfaWQiOiIxIn0.Y1j7d667DXiHjQiE-EYrG3gFWy05FdxVq86j3KR0eFY"
    if not api_key or "your_label_studio_api_key" in api_key:
        print("[WARNING] Please update LABEL_STUDIO_API_KEY in backend/.env with your actual token from Label Studio User Settings!")
        return

    
    
    try:
        # 2. Initialize Label Studio Client
        client = LabelStudio(
            base_url="http://localhost:8080",
            api_key=api_key
        )
        
        # 3. Retrieve and list all projects
        print("\n--- [Step 1] Listing All Projects ---")
        projects = client.projects.list()
        
        project_list = list(projects)
        print(f"Total projects found: {len(project_list)}")
        
        for proj in project_list:
            print(f" - [Project ID: {proj.id}] Title: {proj.title} (Tasks: {proj.task_number})")
            
        if not project_list:
            print("No projects found. Please create a project via Label Studio UI (http://localhost:8080) first!")
            return
            
        # 4. Choose the project that has tasks, or fall back to the first one
        selected_project = next((proj for proj in project_list if proj.task_number and proj.task_number > 0), project_list[0])
        print(f"\n--- [Step 2] Selected Project: ID={selected_project.id}, Title='{selected_project.title}' ---")
        print("Retrieving tasks inside the project...")
        
        # Fetch tasks using client.tasks.list
        tasks = client.tasks.list(project=selected_project.id)
        task_list = list(tasks)
        print(f"Total tasks found: {len(task_list)}")
        
        for task in task_list:
            print(f" - [Task ID: {task.id}] Data: {task.data}")
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("Please ensure Label Studio is running in Docker and the API key is correct.")

if __name__ == "__main__":
    main()
