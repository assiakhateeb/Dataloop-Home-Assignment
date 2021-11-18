from os import listdir
from os.path import isfile, join
from datetime import datetime
import pandas as pd
import random

import dtlpy as dl  # import Dataloop SDK

if dl.token_expired():
    dl.login()


def create_project_and_dataset(project_name, dataset_name):
    # Create a project
    project = dl.projects.create(project_name=project_name)
    # Adding a dataset inside the project
    dataset = project.datasets.create(dataset_name=dataset_name)


def add_item(dataset, item_path):
    # Upload your photos as items to your dataset.
    # remote_path is your dataset folder directory.
    item = dataset.items.upload(local_path=item_path, remote_path='/dog-car-folder')
    return item


def add_labels(dataset):
    # Define the label with your choice of color in RGB form and key
    labels = [{'label_name': 'class1', 'color': (255, 0, 0)},
              {'label_name': 'class2', 'color': (0, 255, 0)},
              {'label_name': 'key', 'color': (0, 0, 255)}]
    # Add the labels to the Recipe
    dataset.add_labels(label_list=labels)


def add_metadata_to_item(dataset, item_path):
    item = dataset.items.get(filepath=item_path)
    # modify metadata
    item.metadata['user'] = dict()
    item.metadata['user']['UTM'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    # update and reclaim item
    item = item.update()


def add_classification(dataset, label, item_path):
    # Classification Init
    annotation_definition = dl.Classification(label=label)
    # Classify a Single Item
    item = dataset.items.get(filepath=item_path)  # Get item from the platform
    # Create a builder instance
    builder = item.annotations.builder()
    # Classify
    builder.add(annotation_definition=dl.Classification(label=label))
    # Upload classification to the item
    item.annotations.upload(builder)


def add_key_point(x, y, label, item_path, dataset):
    # Init Point
    annotations_definition = dl.Point(x=x, y=y, label=label)
    # Create a Point Annotation
    item = dataset.items.get(filepath=item_path)  # Get item from the platform
    builder = item.annotations.builder()  # Create a builder instance
    builder.add(annotation_definition=dl.Point(x=x,
                                               y=y,
                                               label=label))  # Create point annotation with label and attribute
    item.annotations.upload(builder)  # Upload point to the item


def filter_by_label(dataset):
    filters = dl.Filters()  # Create filters instance
    filters.add_join(field='label', values='class1')  # Filter only annotated items with label 'class1'
    pages = dataset.items.list(filters=filters)  # Get filtered items list in a page object
    # Count the items
    print('Number of filtered items in dataset: {}'.format(pages.items_count))
    # Go over all item and print the properties
    for page in pages:
        for item in page:
            item.print()


def retrive_annotation_points(dataset):
    filters = dl.Filters()  # Create filters instance
    filters.add_join(field='type', values='point')  # Filter only annotated items with point
    pages = dataset.items.list(filters=filters)  # Get filtered items list in a page object
    print('Number of items in dataset: {}'.format(pages.items_count))
    points = []
    for page in pages:
        for item in page:
            points = item.annotations.list()
            item.print()
    points = pd.DataFrame(points)
    print(points)
    return points


def main(project_name, dataset_name, item_path):
    '------------ section 2-a ------------'
    create_project_and_dataset(project_name, dataset_name)

    'prep'
    # get dataset
    dataset = dl.projects.get(project_name=project_name).datasets.get(dataset_name=dataset_name)
    # list all files of a directory
    onlyfiles = [f for f in listdir(item_path) if isfile(join(item_path, f))]
    path = '/dog-car-folder/dogs and cars/'

    '------------ section 2-b ------------'
    add_labels(dataset)  # upload and claim item

    '------------ section 2-c ------------'
    items = add_item(dataset, item_path)

    '------------ section 2-d ------------'
    for i in range(5):
        add_metadata_to_item(dataset, path + onlyfiles[i])

    '------------ section 2-e ------------'
    for i in range(2):
        add_classification(dataset, 'class1', path + onlyfiles[i])

    '------------ section 2-f ------------'
    for i in range(2, 5):
        add_classification(dataset, 'class2', path + onlyfiles[i])

    '------------ section 2-g ------------'
    item = dataset.items.get(filepath=path + onlyfiles[2])  # Get item from the platform
    for i in range(5):
        x = random.randint(0, item.metadata['system']['width'])
        y = random.randint(0, item.metadata['system']['height'])
        add_key_point(x, y, 'key', path + onlyfiles[2], dataset)

    '------------ section 3 ------------'
    filter_by_label(dataset)

    '------------ section 4 ------------'
    retrive_annotation_points(dataset)


if __name__ == '__main__':
    main('SE-project', 'dogs-and-cars', r'C:/Users/yasseen/Desktop/dogs and cars')
