from typing import Optional, List, Dict
import torch.nn as nn
import torch


def classifier_discrepancy(
    predictions1: torch.Tensor, predictions2: torch.Tensor
) -> torch.Tensor:
    r"""The `Classifier Discrepancy` in `Maximum Classiﬁer Discrepancy for Unsupervised Domain Adaptation <https://arxiv.org/abs/1712.02560>`_.
    The classfier discrepancy between predictions :math:`p_1` and :math:`p_2` can be described as:

    .. math::
        d(p_1, p_2) = \dfrac{1}{K} \sum_{k=1}^K | p_{1k} - p_{2k} |,

    where K is number of classes.

    Parameters:
        - **predictions1** (tensor): Classifier predictions :math:`p_1`. Expected to contain raw, normalized scores for each class
        - **predictions2** (tensor): Classifier predictions :math:`p_2`
    """
    return torch.mean(torch.abs(predictions1 - predictions2))


def entropy(predictions: torch.Tensor) -> torch.Tensor:
    r"""Entropy of N predictions :math:`(p_1, p_2, ..., p_N)`.
    The definition is:

    .. math::
        d(p_1, p_2, ..., p_N) = -\dfrac{1}{K} \sum_{k=1}^K \log \left( \dfrac{1}{N} \sum_{i=1}^N p_{ik} \right)

    where K is number of classes.

    Parameters:
        - **predictions** (tensor): Classifier predictions. Expected to contain raw, normalized scores for each class
    """
    return -torch.mean(torch.log(torch.mean(predictions, 0) + 1e-6))


class ImageClassifierHead(nn.Module):
    r"""Classifier Head for MCD.
    Parameters:
        - **in_features** (int): Dimension of input features
        - **num_classes** (int): Number of classes
        - **bottleneck_dim** (int, optional): Feature dimension of the bottleneck layer. Default: 1024

    Shape:
        - Inputs: :math:`(minibatch, F)` where F = `in_features`.
        - Output: :math:`(minibatch, C)` where C = `num_classes`.
    """

    def __init__(
        self, in_features: int, num_classes: int, bottleneck_dim: Optional[int] = 1024
    ):
        super(ImageClassifierHead, self).__init__()
        self.head = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(in_features, bottleneck_dim),
            nn.BatchNorm1d(bottleneck_dim),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(bottleneck_dim, bottleneck_dim),
            nn.BatchNorm1d(bottleneck_dim),
            nn.ReLU(),
            nn.Linear(bottleneck_dim, num_classes),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.head(inputs)

    def get_parameters(self) -> List[Dict]:
        """
        :return: A parameter list which decides optimization hyper-parameters,
            such as the relative learning rate of each layer
        """
        params = [
            {"params": self.head.parameters()},
        ]
        return params
