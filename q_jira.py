from jira import JIRA
from collections import defaultdict
from secure_defs import sec_defs

def jsearch(stack_t):

    j_result = []
    query_t2 = ""
    print('jira 0 checkpoint')
    options = {'server': 'https://jira.ruckuswireless.com'}
    jira = JIRA(options, basic_auth=(sec_defs.JIRA_USERNAME, sec_defs.JIRA_PASSWORD))
    # stack_t = ['ShReceiveData', 'ssh_receive_data_ready',
    #            'itc_process_msgs_internal', 'ssh_in_task',
    #            'task_init', 'start_thread']
    query_t1 = 'project = FI AND issuetype = "Defect TRACKER"'
    print('jira 1 checkpoint')
    query_t2 = [query_t2 + " AND text ~" + '"' + stack_e  + '"' for stack_e in stack_t]
    query_t3 = ' AND "Reason Code" = "Fixed" AND "Fixed in RELEASE" =\
               "FI 08.0.30"'
    print('jira 2 checkpoint')
    query_t2 = ''.join(query_t2)
    query_t2 = query_t2.split(',')
    query_t2 = ','.join(query_t2)
    print("query_t2 ", query_t2)
    full_query = query_t1 + query_t2
    print("Full query is: ", full_query)
    all_matches = jira.search_issues(full_query)
    print("All matches: ", all_matches)
    for issue in all_matches:
        print('Defect: {} : {} '.format(issue, issue.fields.summary))
        issue_url = '<a href=https://jira.ruckuswireless.com/browse/'\
         + issue.key + '>Link to Jira defect</a>'
        print('issue url:', issue_url)
        result_element = '\n' + issue.key + ' ' + issue_url + ' ' + 'Summary: ' +\
                         issue.fields.summary
        print('result_element:', result_element)
        j_result.append(result_element)
        print('j_result is ', j_result)
    return j_result


if __name__ == "__main__":
    main()
