from first_utils import query_prepare, process_classification_actions, get_final_output

def get_query_answer(input_q):
    list_dict = query_prepare(input_q)
    context, link_list, var_proceed = process_classification_actions(list_dict, input_q)
    if var_proceed:
        answer_list = get_final_output(context, list_dict)
    else:
        answer_list = [context]
    return answer_list, link_list, context


# input_query = "what is the strike rate of virat kohli?"
# result = get_query_answer(input_query)
# print(result)