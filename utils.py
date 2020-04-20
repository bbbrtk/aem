def get_value_of_change_vertices(distances, s, o, r_id, i_id):
    # return difference in length of cycle, if > 0 bad, if < 0 good
    c = distances

    now_length = c[s[r_id - 1], s[r_id]] + c[s[r_id], s[(r_id + 1) % 50]]
    new_length = c[s[r_id - 1], o[i_id]] + c[o[i_id], s[(r_id + 1) % 50]]
    return new_length - now_length

def get_value_of_swap_vertices(distances, s, a_v_id, b_v_id):
    # typical case: 1 - A - 2 ... 3 - B - 4   -> 1 - B - 2 ... 3 - A - 4
    # neighbours eg: 33-34 it is 32-33-34-35 -> 1-A-B-4  1-B-A-4
    # first and last: A(0)-B(50) [it is reversed!], 3-B-A-2 -> 3-A-B-2

    one, two, three, four = a_v_id - 1, (a_v_id + 1) % 50, b_v_id - 1, (
            b_v_id + 1) % 50  # -1 is a correct idx in solution ;)
    c = distances

    if a_v_id == 0 and b_v_id == 50 - 1:
        now_length = c[s[three], s[b_v_id]] + c[s[b_v_id], s[a_v_id]] + c[s[a_v_id], s[two]]
        new_length = c[s[three], s[a_v_id]] + c[s[a_v_id], s[b_v_id]] + c[s[b_v_id], s[two]]
    elif b_v_id - a_v_id == 1:
        now_length = c[s[one], s[a_v_id]] + c[s[a_v_id], s[b_v_id]] + c[s[b_v_id], s[four]]
        new_length = c[s[one], s[b_v_id]] + c[s[b_v_id], s[a_v_id]] + c[s[a_v_id], s[four]]
    else:
        now_length = c[s[one], s[a_v_id]] + c[s[a_v_id], s[two]] + c[s[three], s[b_v_id]] + c[s[b_v_id], s[four]]
        new_length = c[s[one], s[b_v_id]] + c[s[b_v_id], s[two]] + c[s[three], s[a_v_id]] + c[s[a_v_id], s[four]]

    return new_length - now_length

def get_value_of_swap_edges(distances, s, swap_a_id, swap_b_id):
    c = distances

    from_e1_v, to_e1_v = s[swap_a_id], s[(swap_a_id + 1) % 50]
    from_e2_v, to_e2_v = s[swap_b_id], s[(swap_b_id + 1) % 50]

    diff = c[from_e1_v, from_e2_v] + c[to_e1_v, to_e2_v] - c[from_e1_v, to_e1_v] - c[from_e2_v, to_e2_v]
    return diff