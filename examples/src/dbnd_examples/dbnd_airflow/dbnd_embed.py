import time

from pprint import pprint

import airflow
import pandas as pd

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from dbnd import log_dataframe, log_metric, task
from dbnd._vendor.pendulum import utcnow


args = {"owner": "airflow", "start_date": airflow.utils.dates.days_ago(2)}

dag = DAG(dag_id="embed_dbnd", default_args=args, schedule_interval=None)


# [START howto_operator_python]
@task
def print_context(ds, **kwargs):
    """Print the Airflow context and ds variable from the context."""
    pprint(kwargs)
    log_metric("asd", 1.1)
    print(ds)
    return "Whatever you return gets printed in the logs"


run_this = PythonOperator(
    task_id="print_the_context",
    provide_context=True,
    python_callable=print_context,
    dag=dag,
)
# [END howto_operator_python]


@task
def stub(stage, test_df=None):
    # type: (str, pd.DataFrame) -> None
    # if random.randint(0, 1):
    #     raise Exception("brrrr")

    log_metric(stage, utcnow())
    log_dataframe("df_" + stage, test_df)


# [START howto_operator_python_kwargs]
def my_sleeping_function(random_base):
    """This is a function that will run within the DAG execution"""
    df = pd.DataFrame(
        {
            "num_legs": [2, 4, 8, 0],
            "num_wings": [2, 0, 0, 0],
            "num_specimen_seen": [10, 2, 1, 8],
        },
        index=["falcon", "dog", "spider", "fish"],
    )
    stub("before", df.sample(n=3, random_state=1))
    time.sleep(random_base)
    stub("after", df.sample(frac=0.5, replace=True, random_state=1))


# Generate 5 sleeping tasks, sleeping from 0.0 to 0.4 seconds respectively
for i in range(5):
    task = PythonOperator(
        task_id="sleep_for_" + str(i),
        python_callable=my_sleeping_function,
        op_kwargs={"random_base": float(i) / 10},
        dag=dag,
    )

    run_this >> task
# [END howto_operator_python_kwargs]

# apply_dbnd_on_dag(dag)


def callable_virtualenv():
    """
    Example function that will be performed in a virtual environment.
    Importing at the module level ensures that it will not attempt to import the
    library before it is installed.
    """
    from colorama import Fore, Back, Style
    from time import sleep

    print(Fore.RED + "some red text")
    print(Back.GREEN + "and with a green background")
    print(Style.DIM + "and in dim text")
    print(Style.RESET_ALL)
    for _ in range(10):
        print(Style.DIM + "Please wait...", flush=True)
        sleep(10)
    print("Finished")


# virtualenv_task = PythonVirtualenvOperator(
#     task_id="virtualenv_python",
#     python_callable=callable_virtualenv,
#     requirements=[
#         "colorama==0.4.0"
#     ],
#     system_site_packages=False,
#     dag=dag,
# )
