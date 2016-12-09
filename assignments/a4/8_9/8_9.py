import errno
import os
from optparse import OptionParser
from lib.galago import GalagoRank

if __name__ == '__main__':
    parser = OptionParser(description='Generate a ranking using Galago')
    parser.set_usage(parser.get_usage().replace('\n', '') + ' <xml_file_input> [q1 ... qn]')
    parser.add_option('-g', '--galago', dest="galago_bin", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/galago/galago-3.10-bin/bin/galago',
                        help='Galago "home" directory')
    parser.add_option('-d', '--document', dest="document_dir", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm',
                        help='Document directory to be indexed')
    parser.add_option('-j', '--judgements', dest="judgements_file", default='/media/erikaris/DATA/ODU/Semester_3/intro_to_info_retrieval/assignments/a4/code-report/cacm.rel',
                      help='File .rel as galago eval judgments')
    parser.add_option('-r', '--result', dest="result_count", default='10', help='Number of result')

    (options, args) = parser.parse_args()
    options = vars(options)

    if len(args) < 2:
        parser.print_help()
        exit()


    out_dir = os.path.abspath('output')

    try: os.makedirs(out_dir)
    except OSError, e:
        if e.errno != errno.EEXIST: raise

    index_dir = os.path.join(os.path.pardir, 'index')
    xml_query_file = os.path.abspath(args[0])
    json_query_file = os.path.join(out_dir, 'query.json')
    rel_file = os.path.join(out_dir, 'result.rel')
    res_file = os.path.join(out_dir, 'result.res')
    eval_file = os.path.join(out_dir, 'result.eval')

    q_ids = []
    if len(args) > 1:
        q_ids = args[1:]

    galago = GalagoRank(options['galago_bin'], options['judgements_file'])
    if galago.index(options['document_dir'], index_dir):
        for q_id in q_ids:
            json_query = galago.build_json_input(xml_query_file, json_query_file, q_id)

            rel_docs = galago.get_relevance_docs(q_id)
            res_docs = galago.search(index_dir, json_query_file, res_file, options['result_count'])

            galago.eval(options['judgements_file'], res_file, eval_file)

            print 'Query #                  = {}'.format(json_query['number'])
            print 'Query String             = {}'.format(json_query['text'])
            print 'Relevant Documents       = {}'.format(', '.join(rel_docs))
            print 'Search Result Documents  = {}'.format(', '.join(res_docs))
            print 'BPREF-1                  = {}'.format(galago.get_bpref_1(rel_docs, res_docs))
            print 'BPREF-2                  = {}'.format(galago.get_bpref_2(rel_docs, res_docs))
