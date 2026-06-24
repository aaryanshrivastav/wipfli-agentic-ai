from ..agents.services.memory_services import *

run_id = start_run(connection)

print(run_id)

finish_run(
    connection,
    run_id
)