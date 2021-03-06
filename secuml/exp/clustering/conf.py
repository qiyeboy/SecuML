# SecuML
# Copyright (C) 2016-2019  ANSSI
#
# SecuML is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# SecuML is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SecuML. If not, see <http://www.gnu.org/licenses/>.

import argparse

from secuml.core.conf import exportFieldMethod
from secuml.core.clustering.conf import algos as clustering_conf
from secuml.exp.conf.annotations import AnnotationsConf
from secuml.exp.conf.dataset import DatasetConf
from secuml.exp.conf.exp import ExpConf
from secuml.exp.conf.features import FeaturesConf


class ClusteringConf(ExpConf):

    def __init__(self, secuml_conf, dataset_conf, features_conf,
                 annotations_conf, core_conf, name=None, parent=None,
                 label='all'):
        ExpConf.__init__(self, secuml_conf, dataset_conf, features_conf,
                         annotations_conf, core_conf, name=name, parent=parent)
        self.label = label

    def fields_to_export(self):
        fields = ExpConf.fields_to_export(self)
        fields.extend([('label', exportFieldMethod.primitive)])
        return fields

    @staticmethod
    def gen_parser():
        parser = argparse.ArgumentParser(
            description='Clustering of the data for data exploration.')
        ExpConf.gen_parser(parser)
        AnnotationsConf.gen_parser(
                    parser,
                    message='''CSV file containing the annotations of some
                               instances, or GROUND_TRUTH to use the ground
                               truth annotations stored in idents.csv.
                               These annotations are used for semi-supervised
                               projections.''')
        parser.add_argument(
                 '--label',
                 choices=['all', 'malicious', 'benign'],
                 default='all',
                 help='''The clustering is built from all the instances in the
                         dataset, or only from the benign or malicious ones.
                         By default, the clustering is built from all the
                         instances. The malicious and benign instances are
                         selected according to the ground-truth stored in
                         idents.csv.''')
        subparsers = parser.add_subparsers(dest='algo')
        subparsers.required = True
        factory = clustering_conf.get_factory()
        for algo in factory.get_methods():
            algo_parser = subparsers.add_parser(algo)
            factory.gen_parser(algo, algo_parser)
        return parser

    @staticmethod
    def from_args(args):
        secuml_conf = ExpConf.secuml_conf_from_args(args)
        dataset_conf = DatasetConf.from_args(args, secuml_conf.logger)
        features_conf = FeaturesConf.from_args(args, secuml_conf.logger)
        annotations_conf = AnnotationsConf(args.annotations_file, None,
                                           secuml_conf.logger)
        core_conf = clustering_conf.get_factory().from_args(args.algo, args,
                                                            secuml_conf.logger)
        conf = ClusteringConf(secuml_conf, dataset_conf, features_conf,
                              annotations_conf, core_conf,
                              name=args.exp_name,
                              label=args.label)
        return conf

    def from_json(conf_json, secuml_conf):
        dataset_conf = DatasetConf.from_json(conf_json['dataset_conf'],
                                             secuml_conf.logger)
        features_conf = FeaturesConf.from_json(conf_json['features_conf'],
                                               secuml_conf.logger)
        annotations_conf = AnnotationsConf.from_json(
                                                 conf_json['annotations_conf'],
                                                 secuml_conf.logger)
        core_conf = None
        if conf_json['core_conf'] is not None:
            core_conf = clustering_conf.get_factory().from_json(
                                                conf_json['core_conf'],
                                                secuml_conf.logger)
        exp_conf = ClusteringConf(secuml_conf, dataset_conf, features_conf,
                                  annotations_conf, core_conf,
                                  name=conf_json['name'],
                                  parent=conf_json['parent'],
                                  label=conf_json['label'])
        exp_conf.exp_id = conf_json['exp_id']
        return exp_conf
