import pt_select
import compare_pt
import unique_history
import utils as tool

if __name__ == '__main__':
    pt_select.select_pt()
    compare_pt.unique_process()
    unique_history.unique_his()
    tool.move_file(tool.DST_FL_UIQ_HIS, tool.PTS_FL)
