import torch
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from art.estimators.certification.smoothed_vision_transformers import PyTorchSmoothedViT
import numpy as np
from torchvision import datasets
from torchvision import transforms

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_cifar_data():
    """
    Get CIFAR-10 data.
    :return: cifar train/test data.
    """
    train_set = datasets.CIFAR10('./data', train=True, download=True)
    test_set = datasets.CIFAR10('./data', train=False, download=True)

    x_train = train_set.data.astype(np.float32)
    y_train = np.asarray(train_set.targets)

    x_test = test_set.data.astype(np.float32)
    y_test = np.asarray(test_set.targets)

    x_train = np.moveaxis(x_train, [3], [1])
    x_test = np.moveaxis(x_test, [3], [1])

    x_train = x_train / 255.0
    x_test = x_test / 255.0

    return (x_train, y_train), (x_test, y_test)


(x_train, y_train), (x_test, y_test) = get_cifar_data()

art_model = PyTorchSmoothedViT(model='vit_small_patch16_224',
                               loss=torch.nn.CrossEntropyLoss(),
                               optimizer=torch.optim.SGD,
                               optimizer_params={"lr": 0.01},
                               input_shape=(3, 32, 32),
                               nb_classes=10,
                               ablation_size=4,
                               replace_last_layer=True,
                               load_pretrained=True,
                               )

scheduler = torch.optim.lr_scheduler.MultiStepLR(art_model.optimizer, milestones=[10, 20], gamma=0.1)
# art_model.fit(x_train, y_train,
#              nb_epochs=30,
#              update_batchnorm=True,
#              scheduler=scheduler,
#              transform=transforms.Compose([transforms.RandomHorizontalFlip()]))

# torch.save(art_model.model.state_dict(), 'trained.pt')
# art_model.model.load_state_dict(torch.load('trained.pt'))
art_model.eval_and_certify(x_test, y_test, size_to_certify=4)
