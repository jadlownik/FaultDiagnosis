import logging
import traceback
from faultdiagnosis import FaultDiagnosis

root = logging.getLogger()
root.setLevel(logging.DEBUG)

fault_diagnosis = FaultDiagnosis()

if __name__ == '__main__':
    try:
        fault_diagnosis.start()
    except Exception as e:
        message = f'{e}\n{traceback.format_exc()}'
        logging.error(message)
