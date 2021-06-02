# Copyright 2020 The OATomobile Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from .batch_preprocessing import batch_transform
from .behavioral_cloning import (
    BehaviouralModel, train_step_bc, evaluate_step_bc)
from .deep_imitative_model import (
    ImitativeModel, train_step_dim, evaluate_step_dim)
from .robust_imitative_planning import RIPAgent
from pprint import pprint


def init_behavioral_model(c):
    kwargs = get_bc_kwargs(c)
    print('Model kwargs:')
    pprint(kwargs)
    return BehaviouralModel(**kwargs).to(kwargs['device'])


def get_bc_kwargs(c):
    return {
        'in_channels': c.model_in_channels,
        'dim_hidden': c.model_dim_hidden,
        'output_shape': c.model_output_shape,
        'device': c.exp_device
    }


def init_imitative_model(c):
    kwargs = get_dim_kwargs(c)
    print('Model kwargs:')
    pprint(kwargs)
    return ImitativeModel(**kwargs).to(kwargs['device'])


def get_dim_kwargs(c):
    return {
        'in_channels': c.model_in_channels,
        'dim_hidden': c.model_dim_hidden,
        'output_shape': c.model_output_shape,
        'device': c.exp_device,
        'num_decoding_steps': c.dim_num_decoding_steps,
        'decoding_lr': c.dim_decoding_lr
    }


def init_rip(c):
    # Init kwargs/config items
    ensemble_kwargs = get_rip_kwargs(c)
    k = ensemble_kwargs['k']
    print('RIP kwargs:')
    pprint(ensemble_kwargs)
    algorithm = c.model_rip_algorithm
    model_name = c.model_name
    full_model_name = f'rip-{algorithm}-{model_name}-k_{k}'
    model_name = ensemble_kwargs['model_name']

    # Init models
    backbone_init_fn, train_step, eval_step = BACKBONE_NAME_TO_CLASS_FNS[
        model_name]
    models = [backbone_init_fn(c) for _ in range(k)]
    print(f'Building RIP agent with algorithm {algorithm}, '
          f'backbone model {model_name}, {k} ensemble members.')
    return (
        RIPAgent(models=models, **ensemble_kwargs), full_model_name,
        train_step, eval_step)


def init_model(c):
    model_name = c.model_name
    rip_algorithm = c.model_rip_algorithm
    if rip_algorithm is None:
        print(f'Training {BACKBONE_NAME_TO_FULL_NAME[model_name]}')
        init_fn, train_step, test_step = (
            BACKBONE_NAME_TO_CLASS_FNS[model_name])
        model = init_fn(c)
        return model, model_name, train_step, test_step
    else:
        return init_rip(c)


def get_rip_kwargs(c):
    return {
        'algorithm': c.model_rip_algorithm,
        'k': c.model_rip_k,
        'model_name': c.model_name,
        'device': c.exp_device,
        'num_decoding_steps': c.dim_num_decoding_steps,
        'decoding_lr': c.dim_decoding_lr
    }


BACKBONE_NAME_TO_KWARGS_FN = {
    'bc': get_bc_kwargs,
    'dim': get_dim_kwargs
}

BACKBONE_NAME_TO_CLASS_FNS = {
    'bc': (init_behavioral_model, train_step_bc, evaluate_step_bc),
    'dim': (init_imitative_model, train_step_dim, evaluate_step_dim),
    # TODO: RIP wrapper on BC (rnn decoder)
    # TODO: RIP with MC Dropout?
}

BACKBONE_NAME_TO_FULL_NAME = {
    'bc': 'Behavioral Cloning',
    'dim': 'Deep Imitative Model'
}
