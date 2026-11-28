#!/usr/bin/env python3
"""Task-run lifecycle CLI regression tests."""
import json,pathlib,subprocess,sys,tempfile
def run(*a):
 p=subprocess.run(a,capture_output=True,text=True)
 if p.returncode:raise AssertionError(f"{a!r}\n{p.stdout}\n{p.stderr}")
 return p.stdout.strip()
def reject(*a,expected):
 p=subprocess.run(a,capture_output=True,text=True)
 assert p.returncode!=0 and expected in p.stderr,p.stderr
def main():
 exe=str(pathlib.Path(sys.argv[1]).resolve())
 with tempfile.TemporaryDirectory(prefix="aurions-taskcli-") as d:
  db=str(pathlib.Path(d)/"runtime.sqlite")
  c=json.loads(run(exe,"task","create",db,"task:research","0.5",'{"max_steps":5}',"cause:request","actor:owner"));rid=c["task_run_id"]
  assert c["state"]=="queued" and c["revision"]==1
  r=json.loads(run(exe,"task","transition",db,rid,"1","running","scheduler","cause:start","actor:runtime","-","-","-"));assert r["revision"]==2
  p=json.loads(run(exe,"task","transition",db,rid,"2","paused","control","cause:pause","actor:owner","checkpoint:one","-","-"));assert p["revision"]==3 and "checkpoint:one" in json.loads(p["checkpoint_refs_json"])
  r=json.loads(run(exe,"task","transition",db,rid,"3","running","control","cause:resume","actor:owner","-","-","-"));assert r["revision"]==4
  done=json.loads(run(exe,"task","transition",db,rid,"4","completed","postcondition","result:done","actor:tester","-","-","-"));assert done["revision"]==5
  ev=json.loads(run(exe,"task","events",db,rid));assert len(ev)==5 and ev[-1]["to_state"]=="completed"
  reject(exe,"task","transition",db,rid,"5","running","retry","cause:retry","actor:runtime","-","-","-",expected="terminal task-run state cannot transition")
  reject(exe,"task","transition",db,rid,"3","paused","control","cause:stale","actor:owner","-","-","-",expected="task-run revision conflict")
  lost=json.loads(run(exe,"task","create",db,"task:recovery","0.1","{}","cause:recover","actor:owner"))
  lost=json.loads(run(exe,"task","transition",db,lost["task_run_id"],"1","lost","heartbeat","cause:lost","actor:runtime","-","-","-"))
  reject(exe,"task","transition",db,lost["task_run_id"],"2","running","recovery","cause:resume","actor:runtime","-","-","-",expected="lost run requires reconciliation_ref")
  recovered=json.loads(run(exe,"task","transition",db,lost["task_run_id"],"2","running","recovery","cause:reconciled","actor:runtime","-","-","reconciliation:verified"));assert recovered["revision"]==3
 return 0
if __name__=="__main__":raise SystemExit(main())
