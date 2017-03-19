# coding: utf-8

import luigi
import luigi.s3

class DockerTask(luigi.Task):
    """
    Clase genérica para ejecutar Tasks dentro de contenedores de Docker
    """


    def run(self):
        logger.debug(self.cmd)

        out = subprocess.check_output(self.cmd, shell=True)

        logger.debug(out)

class SmartExternalTask(luigi.ExternalTask):
    """
    Clase para tratar de manera unificada los Targets locales y en AWS S3
    """
    path = luigi.Parameter()

    run = None
    requires = None

    def output(self):
        if self.path.startswith('s3'):
            return luigi.s3.S3Target(self.path)
        else:
            return luigi.LocalTarget(self.path)

    def exists(self):
        if self.path.startswith('s3'):
            return luigi.s3.S3Target(self.path).exists()
        else:
            return luigi.LocalTarget(self.path).exists()


