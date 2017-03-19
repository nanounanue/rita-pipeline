# coding: utf-8
"""
rita Pipeline 

.. module:: rita

   :synopsis: rita pipeline

.. moduleauthor:: Adolfo De Unánue <nanounanue@gmail.com>
"""

import os

import subprocess

import pandas as pd

import csv

import datetime

import luigi
import luigi.s3

import sqlalchemy

## Variables de ambiente
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

## Obtenemos las llaves de AWS
AWS_ACCESS_KEY_ID =  os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

## Logging
import rita.config_ini

import logging

logger = logging.getLogger("rita.pipeline")


import rita.pipelines.utils

import rita.pipelines.common
from rita.pipelines.common.tasks import DockerTask, SmartExternalTask

class ritaPipeline(luigi.WrapperTask):
    """
    Task principal para el pipeline 
    """

    def requires(self):
        fecha = datetime.date.today() + datetime.timedelta(days=-90)

        year = fecha.year
        month = fecha.month

        yield DownloadRITA(year=2015, month=2)

class DownloadRITA(DockerTask):
    year = luigi.IntParameter()
    month = luigi.IntParameter()

    root_path = luigi.Parameter()
    raw_path = luigi.Parameter()

    @property
    def cmd(self):
        return '''
               docker run --rm --env AWS_ACCESS_KEY_ID={} --env AWS_SECRET_ACCESS_KEY={} rita/download-rita --year {} --month {} --data_path {}/{} 
        '''.format(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, self.year, self.month, self.root_path, self.raw_path)

    def output(self):
        return RITAData(path='{}/{}/{}-{}.zip'.format(self.root_path,
                                                      self.raw_path,
                                                      str(self.month).zfill(2),
                                                      self.year))

class RITAData(SmartExternalTask):
    pass

class RTask(luigi.Task):

    root_path = luigi.Parameter()

    def requires(self):
        return RawData()

    def run(self):
        cmd = '''
              docker run --rm -v rita_store:/rita/data  rita/test-r 
        '''

        logger.debug(cmd)

        out = subprocess.check_output(cmd, shell=True)

        logger.debug(out)

    def output(self):
        return luigi.LocalTarget(os.path.join(os.getcwd(), "data", "hola_mundo_desde_R.psv"))


class PythonTask(luigi.Task):

    def requires(self):
        return RTask()

    def run(self):
        cmd = '''
              docker run --rm -v rita_store:/rita/data  rita/test-python --inputfile {} --outputfile {}
        '''.format(os.path.join("/rita/data", os.path.basename(self.input().path)),
                   os.path.join("/rita/data", os.path.basename(self.output().path)))

        logger.debug(cmd)

        out = subprocess.call(cmd, shell=True)

        logger.debug(out)

    def output(self):
        return luigi.LocalTarget(os.path.join(os.getcwd(), "data", "hola_mundo_desde_python.json"))




