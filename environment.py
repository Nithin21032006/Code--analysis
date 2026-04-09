import os
from typing import Dict, Any, Optional
from models import CodeReviewAction, CodeReviewObservation, PRFile, StepResult
from tasks import TASKS, get_task
from graders import GRADERS


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
        files = [
            PRFile(
                filename=f["filename"],
                content=f["content"],
                changes=f"Added {len(f['content'].splitlines())} lines",
                additions=len(f["content"].splitlines()),
                deletions=0
            )
            for f in sample_pr["files"]
        ]
        
        observation = {
            "pr_title": sample_pr["title"],
            "pr_description": sample_pr["description"],
            "files_changed": [f.dict() for f in files],
            "current_file_index": 0,
            "task_level": level,
            "issues_found_so_far": 0,
            "total_expected_issues": len(sample_pr["files"][0].get("issues", [])),
            "review_complete": False
        }
        
        return observation
    
    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one step of review"""
        self.step_count += 1
        
        # Parse action
        action_obj = CodeReviewAction(**action)
        
        # Process based on action type
        if action_obj.action_type == "review":
            reward, info = self._process_review(action_obj)
        elif action_obj.action_type == "suggest_fix":
            reward, info = self._process_suggestion(action_obj)
        elif action_obj.action_type == "approve":
            reward, info = self._approve()
        elif action_obj.action_type == "reject":
            reward, info = self._reject()
        else:
            reward, info = 0.1, {"error": "Unknown action"}
        
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
    
    def _process_review(self, action: CodeReviewAction) -> tuple:
        """Process a review action and calculate reward"""
        current_file = self.current_task["sample_pr"]["files"][self.current_file_index]
        expected_issues = current_file.get("issues", [])
        
        # Check if this issue was already found
        issue_key = f"{action.line_number}_{action.comment[:50]}"
        if issue_key in self.issues_found:
            return 0.01, {"message": "Duplicate issue", "penalty": True}
        
        # Check if issue matches expected
        matched = False
        for expected in expected_issues:
            if expected["line"] == action.line_number:
                # Check if description matches
                if any(keyword in action.comment.lower() 
                       for keyword in expected["description"].lower().split()):
                    matched = True
                    self.issues_found.append(issue_key)
                    # Reward based on severity
                    severity_bonus = {"critical": 0.3, "error": 0.2, 
                                     "warning": 0.1, "nitpick": 0.05}
                    reward = severity_bonus.get(action.severity, 0.1)
                    return reward, {"message": "Issue correctly identified!"}
        
        if not matched:
            # False positive - small penalty
            return 0.02, {"message": "Issue not found or incorrect", "false_positive": True}
        
        return 0.05, {"message": "Review processed"}
    
    def _process_suggestion(self, action: CodeReviewAction) -> tuple:
        """Process a fix suggestion"""
        if action.suggested_fix:
            # Reward for providing a fix
            fix_length = len(action.suggested_fix)
            reward = min(0.1 + (fix_length / 1000), 0.2)
            return reward, {"message": "Fix suggestion recorded"}
        return 0.03, {"message": "Empty suggestion"}
    
    def _approve(self) -> tuple:
        """Approve the PR"""
        # Calculate final score based on issues found vs expected
        current_file = self.current_task["sample_pr"]["files"][0]
        expected_count = len(current_file.get("issues", []))
        found_count = len(self.issues_found)
        
        if found_count >= expected_count:
            reward = 0.9
            self.review_complete = True
        elif found_count >= expected_count * 0.7:
            reward = 0.7
            self.review_complete = True
        elif found_count >= expected_count * 0.5:
            reward = 0.5
            self.review_complete = True
        else:
            reward = 0.3
            self.review_complete = True
        
        return reward, {"message": "PR approved", "issues_found": found_count, 
                       "expected_issues": expected_count}
    
    def _reject(self) -> tuple:
        """Reject the PR with feedback"""
        reward = 0.1
        self.review_complete = True
        return reward, {"message": "PR rejected - needs more work"}
    
    def _get_observation(self) -> Dict[str, Any]:
        """Get current observation state"""
        current_file = self.current_task["sample_pr"]["files"][self.current_file_index]
        
        return {
            "pr_title": self.current_task["sample_pr"]["title"],
            "pr_description": self.current_task["sample_pr"]["description"],
            "files_changed": [current_file],
            "current_file_index": self.current_file_index,
            "task_level": self.current_task["difficulty"],
            "issues_found_so_far": len(self.issues_found),
            "total_expected_issues": len(current_file.get("issues", [])),
            "review_complete": self.review_complete
        }
    
    def state(self) -> Dict[str, Any]:
        """Get current environment state"""
        return self._get_observation()
    
    def close(self):
        """Clean up resources"""
        pass
