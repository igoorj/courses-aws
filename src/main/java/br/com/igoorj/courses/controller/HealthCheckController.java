package br.com.igoorj.courses.controller;

import br.com.igoorj.courses.service.HealthCheckService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/health")
@RequiredArgsConstructor
public class HealthCheckController {

    private final HealthCheckService service;

    @GetMapping("/teste")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok(this.service.ok());
    }
}
