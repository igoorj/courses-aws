package br.com.igoorj.courses.repository;

import br.com.igoorj.courses.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseRepository extends JpaRepository<Course, Long> {
}
