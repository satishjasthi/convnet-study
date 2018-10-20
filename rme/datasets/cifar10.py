from __future__ import absolute_import

import os
import glob
import pickle
import numpy as np

def one_hotify(labels, nb_classes=None):
    '''
    Converts integer labels to one-hot vectors.

    Arguments:
        labels: numpy array containing integer labels. The labels must be in
        range [0, num_labels - 1].

    Returns:
        one_hot_labels: numpy array with shape (batch_size, num_labels).
    '''
    size = len(labels)
    if nb_classes is None:
        nb_classes = np.max(labels) + 1

    one_hot_labels = np.zeros((size, nb_classes))
    one_hot_labels[np.arange(size), labels] = 1
    return one_hot_labels

def load(data_dir, valid_ratio=0.0, one_hot=True, shuffle=False, dtype='float32'):
  """
  Loads CIFAR-10 pickled batch files, given the files' directory.
  Optionally shuffles samples before dividing training and validation sets.
  Can also apply global contrast normalization and ZCA whitening.

  Arguments:
    data_dir: pickled batch files directory.
    valid_ratio: how much of the training data to hold for validation.
      Default: 0.
    one_hot: if True returns one-hot encoded labels, otherwise, returns
    integers. Default: True.
    shuffle: if True shuffles the data before splitting validation data.
      Default: False.
    gcn: if True applies global constrast normalization. Default: False.
    zca: if True applies ZCA whitening. Default: False.
    dtype: data type of image ndarray. Default: `float32`.

  Returns:
    train_set: dict containing training data with keys `data` and `labels`.
    valid_set: dict containing validation data with keys `data` and `labels`.
    test_set: dict containing test data with keys `data` and `labels`.
    If zca == True, also returns
      mean: the computed mean values for each input dimension.
      whitening: the computed ZCA whitening matrix.
      For more information please see datasets.utils.zca_whitening.
   """
  assert valid_ratio < 1 and valid_ratio >= 0, 'valid_ratio must be in [0, 1)'
  files = glob.glob(os.path.join(data_dir, 'data_batch_*'))
  assert len(files) == 5, 'Could not find files!'
  files = [os.path.join(data_dir, 'data_batch_%d' %(i+1)) for i in range(5)]
  data_set = None
  labels = None
  # Iterate over the batches
  for f_name in files:
    with open(f_name, 'rb') as f:
      # Get batch data
      batch_dict = pickle.load(f)
    if data_set is None:
      # Initialize the dataset
      data_set = batch_dict['data'].astype(dtype)
    else:
      # Stack all batches together
      data_set = np.vstack((data_set, batch_dict['data'].astype(dtype)))

    # Get the labels
    # If one_hot, transform all integer labels to one hot vectors
    if one_hot:
      batch_labels = one_hotify(batch_dict['labels'])
    else:
      # If not, just return the labels as integers
      batch_labels = np.array(batch_dict['labels'])
    if labels is None:
      # Initalize labels
      labels = batch_labels
    else:
      # Stack labels together
      labels = np.concatenate((labels, batch_labels), axis=0)

  N = data_set.shape[0]
  if shuffle:
    # Shuffle and separate between training and validation set
    new_order = np.random.permutation(np.arange(N))
    data_set = data_set[new_order]
    labels = labels[new_order]

  # Get the number of samples on the training set
  M = int((1 - valid_ratio)*N)
  # Divide the samples
  train_set, valid_set = {}, {}
  # Reassing the data and reshape it as images
  train_set['data'] = data_set[:M].reshape(
                      (-1, 3, 32, 32)).transpose((0, 2, 3, 1))
  #train_set['data'] = data_set[:M]
  train_set['labels'] = labels[:M]
  valid_set['data'] = data_set[M:].reshape(
                      (-1, 3, 32, 32)).transpose((0, 2, 3, 1))
  valid_set['labels'] = labels[M:]

  test_set = {}
  # Get the test set
  f_name = os.path.join(data_dir, 'test_batch')
  with open(f_name, 'rb') as f:
    batch_dict = pickle.load(f)
    test_set['data'] = batch_dict['data'].astype(dtype).reshape(
                       (-1, 3, 32, 32)).transpose((0, 2, 3, 1))
    if one_hot:
      test_set['labels'] = one_hotify(batch_dict['labels'])
    else:
      test_set['labels'] = np.array(batch_dict['labels'])

  return train_set, valid_set, test_set


def preprocess(dataset):
    mean = np.array([125.3, 123.0, 113.9])
    std = np.array([63.0, 62.1, 66.7])

    dataset -= mean
    dataset /= std

    return dataset
