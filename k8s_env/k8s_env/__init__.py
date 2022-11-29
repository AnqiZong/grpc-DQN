from gym.envs.registration import register

register(
    id='k8s_env-v0',
    entry_point='k8s_env.envs:K8sEnv'
)