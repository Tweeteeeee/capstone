# -*- encoding: utf-8 -*-
# stub: file-dependencies 0.1.6 ruby lib

Gem::Specification.new do |s|
  s.name = "file-dependencies".freeze
  s.version = "0.1.6"

  s.required_rubygems_version = Gem::Requirement.new(">= 0".freeze) if s.respond_to? :required_rubygems_version=
  s.require_paths = ["lib".freeze]
  s.authors = ["Richard Pijnenburg".freeze]
  s.date = "2015-02-18"
  s.description = "manage file dependencies for gems".freeze
  s.email = ["richard.pijnenburg@elasticsearch.com".freeze]
  s.executables = ["file-deps".freeze]
  s.files = ["bin/file-deps".freeze]
  s.homepage = "https://github.com/electrical/file-dependencies".freeze
  s.licenses = ["APACHE 2.0".freeze]
  s.rubygems_version = "2.6.13".freeze
  s.summary = "manage file dependencies for gems".freeze

  s.installed_by_version = "2.6.13" if s.respond_to? :installed_by_version

  if s.respond_to? :specification_version then
    s.specification_version = 4

    if Gem::Version.new(Gem::VERSION) >= Gem::Version.new('1.2.0') then
      s.add_runtime_dependency(%q<minitar>.freeze, [">= 0"])
      s.add_development_dependency(%q<rake>.freeze, ["~> 10.2"])
      s.add_development_dependency(%q<rspec>.freeze, [">= 0"])
      s.add_development_dependency(%q<stud>.freeze, [">= 0"])
      s.add_development_dependency(%q<webmock>.freeze, [">= 0"])
      s.add_development_dependency(%q<coveralls>.freeze, [">= 0"])
      s.add_development_dependency(%q<codeclimate-test-reporter>.freeze, [">= 0"])
    else
      s.add_dependency(%q<minitar>.freeze, [">= 0"])
      s.add_dependency(%q<rake>.freeze, ["~> 10.2"])
      s.add_dependency(%q<rspec>.freeze, [">= 0"])
      s.add_dependency(%q<stud>.freeze, [">= 0"])
      s.add_dependency(%q<webmock>.freeze, [">= 0"])
      s.add_dependency(%q<coveralls>.freeze, [">= 0"])
      s.add_dependency(%q<codeclimate-test-reporter>.freeze, [">= 0"])
    end
  else
    s.add_dependency(%q<minitar>.freeze, [">= 0"])
    s.add_dependency(%q<rake>.freeze, ["~> 10.2"])
    s.add_dependency(%q<rspec>.freeze, [">= 0"])
    s.add_dependency(%q<stud>.freeze, [">= 0"])
    s.add_dependency(%q<webmock>.freeze, [">= 0"])
    s.add_dependency(%q<coveralls>.freeze, [">= 0"])
    s.add_dependency(%q<codeclimate-test-reporter>.freeze, [">= 0"])
  end
end
