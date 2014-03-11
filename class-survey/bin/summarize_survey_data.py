#! /usr/bin/env python

import os
import sys

from pymsbayes import plotting

class StudentResult(object):
    valid_answers = [0, 1]
    def __init__(self, graduate, answers,
            year = None):
        self.answers = answers
        self.graduate = graduate
        self.year = year

    def _set_answers(self, answers):
        self._answers = [int(a) for a in answers]
        for a in self._answers:
            assert a in self.valid_answers

    def _get_answers(self):
        return self._answers

    answers = property(_get_answers, _set_answers)

    def _get_number_of_questions(self):
        return len(self.answers)

    number_of_questions = property(_get_number_of_questions)

    def _get_number_correct(self):
        return sum(self.answers)

    number_correct = property(_get_number_correct)

    def _get_number_wrong(self):
        return self.number_of_questions - self.number_correct

    number_wrong = property(_get_number_wrong)

    def _set_graduate(self, g):
        if g is None:
            raise ValueError('None is not a valid value for graduate')
        self._graduate = False
        if (g is True) or (int(g) > 0):
            self._graduate = True

    def _get_graduate(self):
        return self._graduate

    graduate = property(_get_graduate, _set_graduate)

    def _set_undergraduate(self, g):
        if g is None:
            raise ValueError('None is not a valid value')
        self._graduate = True
        if (g is True) or (int(g) > 0):
            self._graduate = False

    def _get_undergraduate(self):
        return (not self._get_graduate())

    undergraduate = property(_get_undergraduate, _set_undergraduate)

    def _set_year(self, y):
        self._year = None
        if y and (int(y) > 0):
            self._year = int(y)

    def _get_year(self):
        return self._year

    year = property(_get_year, _set_year)

class TestResult(object):
    def __init__(self, table_file_path):
        self.path = table_file_path
        self.number_of_questions = None
        self.number_of_students = None
        self.results = []
        self._parse_table()

    def _parse_table(self, sep='\t'):
        file_stream = open(self.path, 'rU')
        self._parse_header(file_stream)
        if not self.header[0:2] == ['graduate', 'year']:
            raise Exception('table file {0!r} is not valid'.format(self.path))
        self.number_of_questions = len(self.header) - 2
        for line in file_stream:
            if line.strip() == '':
                continue
            l = [c.strip() for c in line.strip().split(sep)]
            r = StudentResult(graduate = l[0],
                    year = l[1],
                    answers = l[2:])
            assert r.number_of_questions == self.number_of_questions
            self.results.append(r)
        self.number_of_students = len(self.results)

    def _parse_header(self, file_stream, sep='\t'):
        header_line = None
        try:
            header_line = file_stream.next()
        except StopIteration:
            file_stream.close()
            raise Exception('did not find header in {0}'.format(file_stream.name))
        self.header = [c.strip().lower() for c in header_line.strip().split(sep)]

    def get_question_results(self, question_index):
        if not question_index in range(self.number_of_questions):
            raise ValueError('question index {0} is out of bounds'.format(
                    question_index))
        ncorrect = 0
        for r in self.results:
            ncorrect += r.answers[question_index]
        return ncorrect, self.number_of_students - ncorrect
    
    def get_question_proportions(self, question_index):
        ncorrect, nwrong = self.get_question_results(question_index)
        assert ncorrect + nwrong == self.number_of_students
        d = float(self.number_of_students)
        return (ncorrect / d), (nwrong / d)

    def question_result_iter(self):
        for q in range(self.number_of_questions):
            yield self.get_question_results(q)

    def overall_result_iter(self):
        for r in self.results:
            yield r.number_correct


class ClassResult(object):
    def __init__(self, before_table_file_path, after_table_file_path,
            question_offset = 2):
        self.before_path = before_table_file_path
        self.after_path = after_table_file_path
        self.before_result = TestResult(self.before_path)
        self.after_result = TestResult(self.after_path)
        assert (self.before_result.number_of_questions == 
                self.after_result.number_of_questions)
        self.number_of_questions = self.after_result.number_of_questions
        self.question_offset = question_offset

    def get_question_plot(self, question_index):
        bpc, bpw = self.before_result.get_question_proportions(question_index)
        apc, apw = self.after_result.get_question_proportions(question_index)
        dc = apc - bpc
        plot_text = r'$\Delta correct = {0}$'.format(dc)
        sbd = plotting.StackedBarData(
                top_values = [bpc, apc],
                bottom_values = [bpw, apw],
                labels = ['before', 'after'],
                width = 0.5,
                orientation = 'vertical',
                top_color = '0.75',
                bottom_color = '0.35',
                top_label = 'correct',
                bottom_label = 'incorrect',
                label_size = 12.0,
                measure_tick_label_size = 10.0,
                extra_plot_space = 0.6)
        sp = plotting.ScatterPlot(
                stacked_bar_data_list = [sbd],
                plot_label = None,
                x_label = None,
                y_label = None,
                y_label_size = 12.0)
                # right_text = plot_text)
        pg = plotting.PlotGrid(
            subplots = [sp],
            num_columns = 1,
            label_schema = None,
            title = 'Question {0}'.format(question_index + self.question_offset),
            title_top = True,
            title_size = 14.0,
            y_title = 'Proportion',
            y_title_position = 0.001,
            y_title_size = 12.0,
            height = 4.0,
            width = 6.0,
            auto_height = False)
        pg.margin_left = 0.04
        pg.margin_right = 1
        pg.margin_bottom = 0
        pg.margin_top = 0.95
        pg.auto_adjust_margins = False
        pg.reset_figure()
        return pg

    def question_plot_iter(self):
        for q in range(self.number_of_questions):
            yield self.get_question_plot(q)

def main():
    import project_util
    years = os.listdir(project_util.DATA_DIR)
    for y in years:
        pdir = os.path.join(project_util.PLOT_DIR, y)
        if not os.path.exists(pdir):
            os.mkdir(pdir)
        results = ClassResult(
                before_table_file_path = os.path.join(project_util.DATA_DIR, y,
                        'pre-class-data.txt'),
                after_table_file_path = os.path.join(project_util.DATA_DIR, y,
                        'post-class-data.txt'),
                question_offset = 2)
        for i, p in enumerate(results.question_plot_iter()):
            out_path = os.path.join(pdir,
                    'question-{0}.pdf'.format(i + results.question_offset))
            p.savefig(out_path)

if __name__ == '__main__':
    main()

