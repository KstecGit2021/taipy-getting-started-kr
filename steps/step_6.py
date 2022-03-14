from statsmodels.tsa.ar_model import AutoReg

from step_4 import *
from step_3 import cleaned_dataset_cfg, nb_predictions_cfg, day_cfg, group_by_cfg, predictions_cfg, pd

# This is the function that will be used by the task
def predict_ml(cleaned_dataset: pd.DataFrame, nb_predictions: int, day: dt.datetime, group_by: str):
    print("     Predicting with ML")
    # Selecting the train data
    train_dataset = cleaned_dataset[cleaned_dataset['Date'] < day]
    
    # Choosing the lags based on the 'group_by'
    if group_by == "original":
        lags = 40
    elif group_by == "day":
        lags = 7
    elif group_by == "week":
        lags = 4
    elif group_by == "month":
        lags = 1
    
    # Fitting the AutoRegressive model
    model = AutoReg(train_dataset['Value'], lags=lags).fit()
    
    # Getting the nb_predictions forecasts
    predictions = model.forecast(nb_predictions).reset_index(drop=True)
    return predictions

# This is the task configuration if the predict_ml function.
# We use the same input and ouput as the previous predict_baseline task but we change the funtion
predict_ml_task_cfg = tp.configure_task(id="predict_ml",
                                        function=predict_ml,
                                        input=[cleaned_dataset_cfg, nb_predictions_cfg, day_cfg, group_by_cfg],
                                        output=predictions_cfg)

# We create a ml pipeline that will clean and predict with the ml model
ml_pipeline_cfg = tp.configure_pipeline(id="ml", task_configs=[clean_data_task_cfg, predict_ml_task_cfg])


# We configure our scenario which is our business problem. Different scenarios would represent different solution to our business problem.
# Here, our scenario is influenced by the group_by, day and number of predictions.
# We have two pipelines in our scenario (baseline and ml), they represent our different models
scenario_cfg = tp.configure_scenario(id="scenario", pipeline_configs=[baseline_pipeline_cfg, ml_pipeline_cfg]) 

# The configuration is now complete, we will not come back to it later.

if __name__=='__main__':
    # We create the scenario
    scenario = tp.create_scenario(scenario_cfg)
    # We execute it
    tp.submit(scenario)
    # We get the resulting scenario
    
    # We print the predictions of the two pipelines
    print("\nBaseline predictions\n", scenario.baseline.predictions.read())
    print("\nModel predictions\n", scenario.ml.predictions.read())        