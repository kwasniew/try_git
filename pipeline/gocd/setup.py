#!/usr/bin/env python
from gomatic import *

def task(pipeline, name, action):
	stage = pipeline.ensure_stage(name)
	job = stage.ensure_job(name)
	job.add_task(ExecTask(['echo', action]))

def scripted_task(pipeline, name, script):
	stage = pipeline.ensure_stage(name)
	job = stage.ensure_job(name)
	job.add_task(ExecTask([script]))

def manual_task(pipeline, name, action):
	stage = pipeline.ensure_stage(name).set_has_manual_approval()
	job = stage.ensure_job(name)
	job.add_task(ExecTask(['echo', action]))

go_server = GoServer(HostRestClient("178.62.106.44:8153"))

pipeline = go_server \
    .ensure_pipeline_group("textbook_parallel_pipelines") \
    .ensure_replacement_of_pipeline("commit_pipeline") \
    .set_git_url("https://github.com/kwasniew/try_git.git")
scripted_task(pipeline, "compile", "./pipeline/commit/compile.sh")
scripted_task(pipeline, "commit_tests", "./pipeline/commit/commit_tests.sh")
scripted_task(pipeline, "assemble", "./pipeline/commit/assemble.sh")
scripted_task(pipeline, "code_analysis", "./pipeline/commit/code_analysis.sh")
scripted_task(pipeline, "binary_repo", "./pipeline/commit/binary_repo.sh")

pipeline = go_server \
    .ensure_pipeline_group("textbook_parallel_pipelines") \
    .ensure_replacement_of_pipeline("acceptance_pipeline") \
    .ensure_material(PipelineMaterial("commit_pipeline", "binary_repo", "app_artifact"))
task(pipeline, "configure_env", "Configure environment")
task(pipeline, "deploy_binaries", "Deploy binaries from artifact repository")
task(pipeline, "smoke_test", "Smoke test")
task(pipeline, "acceptance_test", "Acceptance tests")
task(pipeline, "binary_repo", "Send metadata (acceptance stage passed) to artifact repository")

pipeline = go_server \
    .ensure_pipeline_group("textbook_parallel_pipelines") \
    .ensure_replacement_of_pipeline("uat_pipeline") \
    .set_automatic_pipeline_locking() \
    .ensure_material(PipelineMaterial("acceptance_pipeline", "binary_repo", "app_artifact"))
manual_task(pipeline, "configure_env", "Configure environment")
task(pipeline, "deploy_binaries", "Deploy binaries from artifact repository")
task(pipeline, "smoke_test", "Smoke test")
task(pipeline, "binary_repo", "Send metadata (uat stage passed) to artifact repository")

pipeline = go_server \
    .ensure_pipeline_group("textbook_parallel_pipelines") \
    .ensure_replacement_of_pipeline("capacity_pipeline") \
    .ensure_material(PipelineMaterial("acceptance_pipeline", "binary_repo", "app_artifact"))
task(pipeline, "configure_env", "Configure environment")
task(pipeline, "deploy_binaries", "Deploy binaries from artifact repository")
task(pipeline, "smoke_test", "Smoke test")
task(pipeline, "capacity_test", "Capacity tests")
task(pipeline, "binary_repo", "Send metadata (capacity stage passed) to artifact repository")

pipeline = go_server \
    .ensure_pipeline_group("textbook_parallel_pipelines") \
    .ensure_replacement_of_pipeline("production_pipeline") \
    .set_automatic_pipeline_locking() \
    .ensure_material(PipelineMaterial("acceptance_pipeline", "binary_repo", "app_artifact"))
manual_task(pipeline, "configure_env", "Configure environment")
task(pipeline, "deploy_binaries", "Deploy binaries from artifact repository")
task(pipeline, "smoke_test", "Smoke test")
task(pipeline, "binary_repo", "Send metadata (production stage passed) to artifact repository")


# stage = pipeline.ensure_stage("acceptance_stage")
# job = stage.ensure_job("acceptance_job")
# job.add_task(ExecTask(['echo', 'Configure environment']))
# job.add_task(ExecTask(['echo', 'Deploy binaries from artifact repository']))
# job.add_task(ExecTask(['echo', 'Smoke test']))
# job.add_task(ExecTask(['echo', 'Acceptance tests']))
# job.add_task(ExecTask(['echo', 'Send metadata (acceptance stage passed) to artifact repository']))

# stage = pipeline.ensure_stage("uat_stage").set_has_manual_approval().set_fetch_materials(False)
# job = stage.ensure_job("uat_job")
# job.add_task(ExecTask(['echo', 'Configure environment']))
# job.add_task(ExecTask(['echo', 'Deploy binaries from artifact repository']))
# job.add_task(ExecTask(['echo', 'Smoke test']))
# job.add_task(ExecTask(['echo', 'Send metadata (uat stage passed) to artifact repository']))

# stage = pipeline.ensure_stage("capacity_stage").set_fetch_materials(False)
# job = stage.ensure_job("capacity_job")
# job.add_task(ExecTask(['echo', 'Configure environment']))
# job.add_task(ExecTask(['echo', 'Deploy binaries from artifact repository']))
# job.add_task(ExecTask(['echo', 'Smoke test']))
# job.add_task(ExecTask(['echo', 'Capacity tests']))
# job.add_task(ExecTask(['echo', 'Send metadata (capacity stage passed) to artifact repository']))

# stage = pipeline.ensure_stage("production_stage").set_has_manual_approval().set_fetch_materials(False)
# job = stage.ensure_job("production_job")
# job.add_task(ExecTask(['echo', 'Configure environment']))
# job.add_task(ExecTask(['echo', 'Deploy binaries from artifact repository']))
# job.add_task(ExecTask(['echo', 'Smoke test']))
# job.add_task(ExecTask(['echo', 'Send metadata (production stage passed) to artifact repository']))

go_server.save_updated_config(save_config_locally=True, dry_run=False)