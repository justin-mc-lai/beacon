# User Stories: beacon-goal-durable-supervisor-v167

## US-DGS-01 续跑

**作为** 使用 beacon-goal 的开发者  
**我希望** 会话断了之后用 resume-pack 知道 next_action  
**以便** 不重头跑也不靠聊天记忆  

Maps: W-DGS-LEGAL-02, AC-DGS-004, AC-DGS-006

## US-DGS-02 可选监督

**作为** 需要长程交付的用户  
**我希望** 显式 `goal supervise` 挂上监督（默认 2 分钟心跳）  
**以便** 空闲 stall 被发现且可选驱动 qa/ralph  

Maps: W-DGS-LEGAL-03, AC-DGS-001, AC-DGS-002, AC-DGS-007

## US-DGS-03 证据链

**作为** 评审者  
**我希望** execution.jsonl 追加可查  
**以便** 审计中间过程；complete 仍只认 verifier  

Maps: AC-DGS-003, AC-DGS-008, AC-DGS-011

## US-DGS-04 非法自证

**作为** 系统  
**我拒绝** 中断态直 complete、无 scorecard 自证、run 时偷偷 auto-supervise  

Maps: I-DGS-001..005, AC-DGS-008, AC-DGS-001
