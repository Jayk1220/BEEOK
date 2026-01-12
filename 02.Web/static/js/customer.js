/**
 * 고객 관리 시스템 전용 자바스크립트
 */
document.addEventListener("DOMContentLoaded", function() {
    
    // 1. 플래시 메시지 자동 삭제 (3초 후)
    const alerts = document.querySelectorAll('.auto-dismiss');
    
    alerts.forEach(function(alert) {
        // 3초 대기 후 실행
        setTimeout(function() {
            // 서서히 사라지는 효과 적용
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            
            // 애니메이션 완료 후 요소 제거
            setTimeout(function() {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        }, 3000); 
    });

    // 2. 검색창 초기화 기능 (필요 시 추가 활용 가능)
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        console.log("고객 목록 검색 시스템 활성화");
    }
});