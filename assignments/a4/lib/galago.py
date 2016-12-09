import json
import os
from math import log
from subprocess import Popen, PIPE, call
from threading import Thread
import xmltodict


class Command(object):
    def __init__(self, cmd, out_pipe_callback=None, err_pipe_callback=None):
        self.cmd = cmd
        self.process = None
        self.out_pipe_callback = out_pipe_callback
        self.err_pipe_callback = err_pipe_callback

    def run(self, timeout, args=()):
        def target():
            self.process = Popen(self.cmd, stdout=PIPE, stderr=PIPE)

            if self.out_pipe_callback:
                stdout_thread = Thread(target=self.out_pipe_callback,
                                   args=(self.process.stdout, ) + args)
                stdout_thread.daemon = True
                stdout_thread.start()

            if self.err_pipe_callback:
                stderr_thread = Thread(target=self.err_pipe_callback,
                                      args=(self.process.stderr, ) + args)
                stderr_thread.daemon = True
                stderr_thread.start()

            self.process.wait()

        thread = Thread(target=target)
        thread.daemon = True
        thread.start()

        thread.join(timeout)
        try: self.process.terminate()
        except: pass

        return self.process.returncode


class GalagoRank(object):
    galago_bin = None
    rel_docs = {}
    res_docs = []

    def __init__(self, galago_bin, judgements_file):
        self.galago_bin = galago_bin
        self.rel_docs = self.build_relevance(judgements_file)

    def index(self, document_dir, index_dir):
        if not os.path.exists(index_dir):
            bash = '"{}" build --indexPath="{}" --inputPath="{}"'.format(
                self.galago_bin, index_dir, document_dir)

            code = call(['bash', '-c', bash])
            return code == 0

        else:
            return True

    def build_relevance(self, judgements_file):
        with open(judgements_file, 'r') as fp:
            rel_docs = {}
            for line in fp.readlines():
                q, a, doc, b = line.split()

                rel_docs.setdefault(q, [])
                rel_docs[q].append(doc)

            return rel_docs
        return {}

    def get_relevance_docs(self, q=None):
        if q:
            if str(q) in self.rel_docs:
                return self.rel_docs[str(q)]
            else:
                return []
        else:
            rel_docs = []
            for q, docs in self.rel_docs.items():
                rel_docs += docs

            return rel_docs


    def get_result_docs(self):
        return self.res_docs

    def build_json_input(self, xml_query_file, json_query_file, id=None):
        json_query = json.dumps(xmltodict.parse(open(xml_query_file).read()))
        json_query = json.loads(json_query)
        json_query = json_query['parameters']

        if id:
            selected_json_query = {}
            selected_json_query.setdefault('query', [])
            for query in json_query['query']:
                if query['number'] == str(id):
                    selected_json_query['query'].append({
                        'number' : str(id),
                        'text' : query['text']
                    })
        else:
            selected_json_query = json_query

        open(json_query_file, 'wb').write(json.dumps(selected_json_query))

        if id:
            return selected_json_query['query'][0]
        else:
            return selected_json_query['query']

    def search(self, index_dir, json_query_file, result_file, count):
        res_docs = []

        cmd = Command([self.galago_bin, 'batch-search', '--index={}'.format(index_dir),
                       '--requested={}'.format(count), '{}'.format(json_query_file)],
                      self.search_result)
        cmd.run(60 * 10, args=(res_docs, result_file, ))

        return res_docs

    def search_result(self, out, res_docs, result_file):
        lines = []
        if out and hasattr(out, 'readline'):
            for line in iter(out.readline, b''):
                line = line.strip()
                q_id, a, doc, id, score, b = self.search_parse(line)
                lines.append((q_id, a, doc, id, score, b))
                res_docs.append(doc)

        with open(result_file, 'wb') as fp:
            fp.write('\n'.join([' '.join(l) for l in lines]))
            fp.close()

    def search_parse(self, line):
        parts = line.split()
        if len(parts) == 6:
            q_id, a, doc, id, score, b = parts
        else:
            q_id = parts[0]
            a = parts[1]
            doc = ' '.join(parts[2:len(parts)-3])
            id = parts[len(parts) - 3]
            score = parts[len(parts) - 2]
            b = parts[len(parts) - 1]

        doc = os.path.basename(doc)
        doc = os.path.splitext(doc)[0]
        return q_id, a, doc, id, score, b

    def eval(self, rel_file, res_file, eval_file):
        bash = '{} eval --judgments="{}" --baseline="{}" > "{}"'.format(
            self.galago_bin, rel_file, res_file, eval_file)

        cmd = Command(['bash', '-c', bash])
        code = cmd.run(60 * 10)

        return code == 0

    def get_precision(self, rel_docs, res_docs):
        relset = set(rel_docs)
        retrset = set(res_docs)

        if len(retrset) > 0:
            return float(len(relset.intersection(retrset))) / len(retrset)
        else:
            return 0

    def get_recall(self, rel_docs, res_docs):
        relset = set(rel_docs)
        retrset = set(res_docs)

        if len(relset) > 0:
            return float(len(relset.intersection(retrset))) / len(relset)
        else:
            return 0

    def get_all_precisions(self, rel_docs, res_docs):
        rr = []
        for i in range(1, len(res_docs) + 1):
            rr.append(self.get_precision(rel_docs, res_docs[:i]))

        return rr

    def get_all_recalls(self, rel_docs, res_docs):
        rr = []
        for i in range(1, len(res_docs) + 1):
            rr.append(self.get_recall(rel_docs, res_docs[:i]))

        return rr

    def get_map(self, rel_docs, res_docs):
        rr = self.get_all_precisions(rel_docs, res_docs)

        res = []
        for i in range(len(res_docs)):
            if res_docs[i] in rel_docs:
                res.append(rr[i])

        if len(res) == 0:
            return 0.0

        return float(sum(res)) / len(res)

    def get_relevance(self, i, rel_docs, res_docs):
        return 1 if res_docs[i] in rel_docs else 0

    def get_dcg(self, p, rel_docs, res_docs):
        sum = 0
        for i in range(2, p + 1):
            sum += float(self.get_relevance(i-1, rel_docs, res_docs)) / log(i, 2)
        return self.get_relevance(0, rel_docs, res_docs) + sum

    def get_idcg(self, p):
        sum = 0
        for i in range(2, p + 1):
            sum += 1 / log(i, 2)
        return 1 + sum

    def get_ndcg(self, p, rel_docs, res_docs):
        dcg = self.get_dcg(p, rel_docs, res_docs)
        idcg = self.get_idcg(p)
        return dcg / idcg

    def get_reciprocal_rank(self, rel_docs, res_docs):
        for i in range(1, len(res_docs) + 1):
            if res_docs[i - 1] in rel_docs:
                return 1.0 / i
        return 0.0

    def get_r_precision(self, rel_docs, res_docs):
        return self.get_all_precisions(rel_docs, res_docs)[len(rel_docs)-1]

    def get_bpref_1(self, rel_docs, res_docs):
        """calculate BPREF as the first equation in the textbook"""

        relset = set(rel_docs)
        retrset = set(res_docs)

        R = float(len(rel_docs))

        res = 0
        for dr in rel_docs:
            if dr not in res_docs:
                Ndr = R
            else:
                Ndr = float(len([doc for doc in res_docs[:res_docs.index(dr)] if doc not in rel_docs]))
            res += (1.0 - Ndr / R)

        return 1.0 / R * res

    def get_bpref_2(self, rel_docs, res_docs):
        """calculate BPREF as the second equation in the textbook"""

        p = 0.0
        q = 0.0

        for dr in rel_docs:
            if dr not in res_docs:
                p += 0
                q += len(res_docs)
            else:
                p += float(len([doc for doc in res_docs[res_docs.index(dr):] if doc not in rel_docs]))
                q += float(len([doc for doc in res_docs[:res_docs.index(dr)] if doc not in rel_docs]))

        return p / (p + q)
