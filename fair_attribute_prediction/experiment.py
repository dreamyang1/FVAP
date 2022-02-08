import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict

from comet_ml import OfflineExperiment, Experiment
from comet_ml.experiment import BaseExperiment
from torch import save
from torch.backends import cudnn

from training import train_classifier
from util import create_dataset, create_dataloader, create_model, create_optimizer, create_lr_scheduler


def log_experiment_status(experiment: BaseExperiment, status: str):
    status_message = f"Experiment '{experiment.get_name()}' {status}"
    print(status_message)
    experiment.send_notification(status_message)


def train_model_experiment(parameters: Dict, experiment_name: str, offline_experiment: bool = False):
    start_date = datetime.utcnow()
    experiment_class = OfflineExperiment if offline_experiment else Experiment
    experiment = experiment_class(
        project_name="fair-attribute-prediction",
        workspace="tobias-haenel",
        auto_metric_logging=False,
        auto_param_logging=False,
    )
    experiment.set_name(experiment_name)
    log_experiment_status(experiment, "started")
    try:
        experiment.log_parameters(parameters)

        if cudnn.is_available():
            cudnn.enabled = False

        train_dataset = create_dataset(parameters, split_name="train")
        valid_dataset = create_dataset(parameters, split_name="valid")

        train_dataloader = create_dataloader(parameters, train_dataset)
        valid_dataloader = create_dataloader(parameters, valid_dataset)

        model = create_model(parameters, train_dataset)
        optimizer = create_optimizer(parameters, model)
        lr_scheduler = create_lr_scheduler(parameters, optimizer)

        best_model_state, final_model_state = train_classifier(
            model,
            optimizer,
            lr_scheduler,
            train_dataloader,
            valid_dataloader,
            parameters,
            experiment,
        )

        experiment_results_dir_path = Path("experiments") / "results" / experiment_name / start_date.isoformat()
        best_model_state_file_path = experiment_results_dir_path / f"best_model.pt"
        final_model_state_file_path = experiment_results_dir_path / f"final_model.pt"
        parameters_file_path = experiment_results_dir_path / f"parameters.pt"
        experiment_results_dir_path.mkdir(parents=True, exist_ok=True)
        save(best_model_state, best_model_state_file_path)
        save(final_model_state, final_model_state_file_path)
        save(parameters, parameters_file_path)

        experiment.log_model("results", str(experiment_results_dir_path))

        log_experiment_status(experiment, "finished successfully")
    except Exception as exception:
        log_experiment_status(experiment, f"finished with errors\n{traceback.format_exc()}")
        experiment.end()
        raise exception

    experiment.end()
    return experiment
