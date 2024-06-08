import schedule
import time
from functions.utils import sheets_creds

def run_task():
    parentID = "1SxQgyExpfopcjYHfIeBFhXLPdAUzM6rE"
    sheetsFileName = "Permissões Gravação"
    sheets_creds(parentID, sheetsFileName)

# Schedule the task to run every hour
schedule.every().hour.do(run_task)

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(3500)