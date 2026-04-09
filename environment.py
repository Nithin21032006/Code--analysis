# environment.py
import os
from typing import Dict, Any, Optional

# Don't import GRADERS at the top - import inside methods to avoid circular imports
from tasks import TASKS, get_task


class CodeReviewEnv:
    def __init__(self):
        self.current_task = None
        self.current_file_index = 0
        self.issues_found = []
        self.review_complete = False
        self.step_count = 0
        
    def reset(self, level: str = "easy") -> Dict[str, Any]:
        """Reset environment to initial state"""
        task = get_task(level)
        if not task:
            return {"error": f"Task '{level}' not found"}
        
        self.current_task = task
        self.current_file_index = 0
        self.issues_found = []
        self.review_complete = False
        self.step_count = 0
        
        # Build initial observation
        sample_pr = task["sample_pr"]
        files = sample_pr["files"]
        
        observation = {
            "pr_title": sample_pr["title"],
            "pr_description": sample_pr["description"],
            "files_changed": files,
            "current_file_index": 0,
            "task_level": level,
            "issues_found_so_far": 0,
            "total_expected_issues": len(files[0].get("issues", [])) if files else 0,
            "review_complete": False
        }
        
        return observation
    
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one step of review"""
        self.step_count += 1
        
        action_type = action.get("action_type", "review")
        comment = action.get("comment", "")
        line_number = action.get("line_number")
        severity = action.get("severity", "warning")
        suggested_fix = action.get("suggested_fix")
        
        # Process based on action type
        if action_type == "review":
            reward, info = self._process_review(comment, line_number, severity)
        elif action_type == "suggest_fix":
            reward, info = self._process_suggestion(suggested_fix)
        elif action_type == "approve":
            reward, info = self._approve()
        elif action_type == "reject":
            reward, info = self._reject()
        else:
            reward, info = 0.05, {"error": f"Unknown action: {action_type}"}
        
        # Check if review is complete
        done = self.review_complete or self.step_count >= 20
        
        # Get current observation
        observation = self._get_observation()
        
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info
        }
    
    def _process_review(self, comment: str, line_number: int, severity: str) -> tuple:
        """Process a review action and calculate reward"""
        if not self.current_task:
            return 0.01, {"error": "No active task"}
            
        files = self.current_task["sample_pr"]["files"]
        if not files or self.current_file_index >= len(files):
            return 0.01, {"error": "No file to review"}
            
        current_file = files[self.current_file_index]
        expected_issues = current_file.get("issues", [])
        
        # Check if this issue was already found
        issue_key = f"{line_number}_{comment[:50]}"
        if issue_key in self.issues_found:
            return 0.01, {"message": "Duplicate issue", "penalty": True}
        
        # Check if issue matches expected
        matched = False
        for expected in expected_issues:
            if expected.get("line") == line_number:
                # Check if description matches
                expected_desc = expected.get("description", "").lower()
                comment_lower = comment.lower()
                
                keywords = expected_desc.split()
                for keyword in keywords[:3]:  # Check first 3 keywords
                    if keyword in comment_lower and len(keyword) > 3:
                        matched = True
                        break
                
                if matched:
                    self.issues_found.append(issue_key)
                    # Reward based on severity
                    severity_bonus = {
                        "critical": 0.30,
                        "error": 0.20, 
                        "warning": 0.10,
                        "nitpick": 0.05
                    }
                    reward = severity_bonus.get(severity, 0.10)
                    return reward, {"message": "Issue correctly identified!"}
        
        if not matched:
            # False positive - small penalty
            return 0.02, {"message": "Issue not found or incorrect", "false_positive": True}
        
        return 0.05, {"message": "Review processed"}
    
    def _process_suggestion(self, suggested_fix: str) -> tuple:
        """Process a fix suggestion"""
        if suggested_fix and len(suggested_fix) > 10:
            # Reward for providing a fix
            fix_length = len(suggested_fix)
            reward = min(0.10 + (fix_length / 1000), 0.20)
            return reward, {"message": "Fix suggestion recorded"}
        return 0.03, {"message": "Empty or too short suggestion"}
    
    def _approve(self) -> tuple:
        """Approve the PR"""
        files = self.current_task["sample_pr"]["files"]
        expected_count = len(files[0].get("issues", [])) if files else 0
        found_count = len(self.issues_found)
        
        if found_count >= expected_count:
            reward = 0.85
            self.review_complete = True
        elif found_count >= expected_count * 0.7:
            reward = 0.70
            self.review_complete = True
        elif found_count >= expected_count * 0.5:
            reward = 0.50
            self.review_complete = True
        else:
            reward = 0.30
            self.review_complete = True
        
        return reward, {"message": "PR approved", "issues_found": found_count, 
                       "expected_issues": expected_count}
    
    def _reject(self) -> tuple:
        """Reject the PR with feedback"""
        reward = 0.15
        self.review_complete = True
        return reward, {"message": "PR rejected - needs more work"}
    
    def _get_observation(self) -> Dict[str, Any]:
        """Get current observation state"""
        if not self.current_task:
            return {"error": "No active task"}
            
        files = self.current_task["sample_pr"]["files"]
        current_file = files[self.current_file_index] if files else {}
        
        return {
            "pr_title": self.current_task["sample_pr"]["title"],
            "pr_description": self.current_task["sample_pr"]["description"],
            "files_changed": [current_file] if current_file else [],
            "current_file_index": self.current_file_index,
            "task_level": self.current_task.get("difficulty", "easy"),
            "issues_found_so_far": len(self.issues_found),
            "total_expected_issues": len(current_file.get("issues", [])) if current_file else 0,
            "review_complete": self.review_complete
        }
    
    def state(self) -> Dict[str, Any]:
        """Get current environment state"""
        return self._get_observation()
    
    def close(self):
        """Clean up resources"""
        pass
